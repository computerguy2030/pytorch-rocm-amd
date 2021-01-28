import os
import sys

import torch
from torch.fx import symbolic_trace, subgraph_rewriter

# Make the helper files in test/ importable
pytorch_test_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(pytorch_test_dir)
from torch.testing._internal.jit_utils import JitTestCase

if __name__ == '__main__':
    raise RuntimeError("This test file is not meant to be run directly, use:\n\n"
                       "\tpython test/test_fx.py TESTNAME\n\n"
                       "instead.")

class TestSubgraphRewriter(JitTestCase):

    def test_subgraph_rewriter_preserves_logic(self):
        class M(torch.nn.Module):
            def forward(self, x):
                val = torch.neg(x) + torch.relu(x)
                return torch.add(val, val)

        def pattern(x):
            return torch.neg(x) + torch.relu(x)

        def comparison(x):
            val = torch.neg(x) + torch.relu(x)
            return torch.add(val, val)

        traced = symbolic_trace(M())
        comparison_fn = symbolic_trace(comparison)

        x = torch.rand(1, 3)

        # Replace `pattern` with the same pattern (shouldn't change
        # the underlying logic)
        subgraph_rewriter.replace_pattern(traced, pattern, pattern)

        traced.graph.lint(traced)

        ref_output = comparison_fn(x)
        test_output = traced.forward(x)
        self.assertEqual(ref_output, test_output)

    def test_subgraph_rewriter_with_oneliner_pattern(self):
        class M(torch.nn.Module):
            def forward(self, x):
                val = torch.neg(x)
                return torch.add(val, val)

        def pattern(x):
            return torch.neg(x)

        def replacement(x):
            return torch.relu(x)

        def comparison(x):
            val = torch.relu(x)
            return torch.add(val, val)

        traced = symbolic_trace(M())
        comparison_fn = symbolic_trace(comparison)

        x = torch.rand(1, 3)

        subgraph_rewriter.replace_pattern(traced, pattern, replacement)

        traced.graph.lint(traced)

        ref_output = comparison_fn(x)
        test_output = traced.forward(x)
        self.assertEqual(ref_output, test_output)

    def test_subgraph_rewriter_single_pattern_match(self):
        class M(torch.nn.Module):
            def forward(self, x):
                val = torch.neg(x) + torch.relu(x)
                return torch.add(val, val)

        def pattern(x):
            return torch.neg(x) + torch.relu(x)

        def replacement(x):
            return torch.relu(x)

        def comparison(x):
            val = torch.relu(x)
            return torch.add(val, val)

        traced = symbolic_trace(M())
        comparison_fn = symbolic_trace(comparison)

        x = torch.rand(1, 3)

        subgraph_rewriter.replace_pattern(traced, pattern, replacement)

        traced.graph.lint(traced)

        ref_output = comparison_fn(x)
        test_output = traced.forward(x)
        self.assertEqual(ref_output, test_output)

    def test_subgraph_rewriter_multiple_pattern_match(self):
        class M(torch.nn.Module):
            def forward(self, x, w1, w2):
                m1 = torch.cat([w1, w2]).sum()
                m2 = torch.cat([w1, w2]).sum()
                return x + torch.max(m1) + torch.max(m2)

        def pattern(w1, w2):
            return torch.cat([w1, w2]).sum()

        def replacement(w1, w2):
            return torch.stack([w1, w2])

        def comparison(x, w1, w2):
            m1 = torch.stack([w1, w2])
            m2 = torch.stack([w1, w2])
            return x + torch.max(m1) + torch.max(m2)

        traced = symbolic_trace(M())
        comparison_fn = symbolic_trace(comparison)

        x = torch.rand(1, 3)
        w1 = torch.rand(1, 3)
        w2 = torch.rand(1, 3)

        subgraph_rewriter.replace_pattern(traced, pattern, replacement)

        traced.graph.lint(traced)

        ref_outs = comparison_fn(x, w1, w2)
        test_outs = traced.forward(x, w1, w2)
        self.assertEqual(ref_outs, test_outs)

    def test_subgraph_rewriter_graph_argument_order(self):
        class M(torch.nn.Module):
            def forward(self, x, y):
                return torch.mm(x, y)

        def pattern(x, y):
            return torch.mm(x, y)

        def comparison(x, y):
            return torch.mm(x, y)

        traced = symbolic_trace(M())
        comparison_fn = symbolic_trace(comparison)

        x = torch.randn(3, 4)
        y = torch.randn(4, 5)

        subgraph_rewriter.replace_pattern(traced, pattern, pattern)

        traced.graph.lint(traced)

        ref_outs = comparison_fn(x, y)
        test_outs = traced.forward(x, y)
        self.assertEqual(ref_outs, test_outs)

    def test_subgraph_rewriter_correct_output_replacement(self):
        class M(torch.nn.Module):
            def forward(self, x, y):
                val = torch.neg(y) + torch.relu(x)
                return torch.add(val, val)

        def pattern(x):
            return torch.relu(x)

        def replacement(x):
            return torch.neg(x)

        def comparison(x, y):
            val = torch.neg(y) + torch.neg(x)
            return torch.add(val, val)

        traced = symbolic_trace(M())
        comparison_fn = symbolic_trace(comparison)

        x = torch.randn(4, 4)
        y = torch.randn(4, 4)

        subgraph_rewriter.replace_pattern(traced, pattern, replacement)

        traced.graph.lint(traced)

        ref_outs = comparison_fn(x, y)
        test_outs = traced.forward(x, y)
        self.assertEqual(ref_outs, test_outs)

    def test_subgraph_rewriter_traced_as_callable(self):
        class M(torch.nn.Module):
            def forward(self, x):
                val = torch.neg(x) + torch.relu(x)
                return torch.add(val, val)

        class Pattern(torch.nn.Module):
            def forward(self, x):
                return torch.neg(x) + torch.relu(x)

        class Replacement(torch.nn.Module):
            def forward(self, x):
                return torch.sigmoid(x)

        def comparison(x):
            val = torch.sigmoid(x)
            return torch.add(val, val)

        traced = symbolic_trace(M())
        traced_pattern = symbolic_trace(Pattern())
        traced_replacement = symbolic_trace(Replacement())
        comparison_fn = symbolic_trace(comparison)

        x = torch.randn(3, 4)

        subgraph_rewriter.replace_pattern(traced, traced_pattern, traced_replacement)

        traced.graph.lint(traced)

        ref_outs = comparison_fn(x)
        test_outs = traced.forward(x)
        self.assertEqual(ref_outs, test_outs)

    def test_subgraph_rewriter_container_output(self):
        class M(torch.nn.Module):
            def forward(self, x):
                a = torch.neg(x)
                return x, torch.add(a, a)

        def pattern(x):
            a = torch.neg(x)
            return x, torch.add(a, a)

        def replacement(x):
            a = torch.sigmoid(x)
            return torch.cat([a, a])

        traced = symbolic_trace(M())
        comparison_fn = symbolic_trace(replacement)

        x = torch.randn(3, 4)

        subgraph_rewriter.replace_pattern(traced, pattern, replacement)

        traced.graph.lint(traced)

        ref_outs = comparison_fn(x)
        test_outs = traced.forward(x)
        self.assertEqual(ref_outs, test_outs)

    def test_subgraph_rewriter_nested_container_output(self):
        class M(torch.nn.Module):
            def forward(self, x):
                a = torch.neg(x)
                return x, (a, x), torch.add(a, a)

        def pattern(x):
            a = torch.neg(x)
            return x, (a, x), torch.add(a, a)

        def replacement(x):
            a = torch.sigmoid(x)
            return torch.cat([a, a])

        traced = symbolic_trace(M())
        comparison_fn = symbolic_trace(replacement)

        x = torch.randn(3, 4)

        subgraph_rewriter.replace_pattern(traced, pattern, replacement)

        traced.graph.lint(traced)

        ref_outs = comparison_fn(x)
        test_outs = traced.forward(x)
        self.assertEqual(ref_outs, test_outs)

    def test_subgraph_rewriter_pattern_is_entire_graph(self):
        class M(torch.nn.Module):
            def forward(self, x):
                a = torch.neg(x)
                return torch.add(a, a)

        def pattern(x):
            a = torch.neg(x)
            return torch.add(a, a)

        def replacement(x):
            a = torch.sigmoid(x)
            return torch.cat([a, a])

        traced = symbolic_trace(M())
        comparison_fn = symbolic_trace(replacement)

        x = torch.randn(3, 4)

        subgraph_rewriter.replace_pattern(traced, pattern, replacement)

        traced.graph.lint(traced)

        ref_outs = comparison_fn(x)
        test_outs = traced.forward(x)
        self.assertEqual(ref_outs, test_outs)

    """
    Big TODO here @ansley
    The problem is that `bilinear_1` (Node) references a "nonexistent
    attribute"--need to figure out how/if we should work around this.
    Will probably submit a separate PR
    """
    # def test_subgraph_rewriter_with_attribute_reference(self):
    #    class M(torch.nn.Module):
    #        def __init__(self):
    #            super(M, self).__init__()
    #            self.linear = torch.nn.Linear(200, 200)

    #        def forward(self, x):
    #            y = self.linear(x)
    #            return torch.add(x, y)

    #    class Pattern(torch.nn.Module):
    #        def __init__(self):
    #            super(Pattern, self).__init__()
    #            self.linear = torch.nn.Linear(200, 200)

    #        def forward(self, x):
    #            return self.linear(x)

    #    class Replacement(torch.nn.Module):
    #        def __init__(self):
    #            super(Replacement, self).__init__()
    #            self.bilinear = torch.nn.Bilinear(200, 200, 200)

    #        def forward(self, x):
    #            return self.bilinear(x)

    #    class Comparison(torch.nn.Module):
    #        def __init__(self):
    #            super(Comparison, self).__init__()
    #            self.bilinear = torch.nn.Bilinear(200, 200, 200)

    #        def forward(self, x):
    #            y = self.bilinear(x)
    #            return torch.add(x, y)

    #    traced = symbolic_trace(M())
    #    comparison = symbolic_trace(Comparison())

    #    x = torch.randn(3, 4)

    #    subgraph_rewriter.replace_pattern(traced, Pattern(), Replacement())

    #    traced.graph.lint(traced)

    #    ref_outs = comparison(x)
    #    test_outs = traced.forward(x)
    #    self.assertEqual(ref_outs, test_outs)
