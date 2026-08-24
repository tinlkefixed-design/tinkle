from __future__ import annotations

import ast
import math

import numpy as np
import sympy as sp
from scipy.linalg import norm

from tinkle.math_engine.schemas import MathMode, MathRequest, MathResult, VerificationResult


class MathematicsEngine:
    """Phase 13 Mathematics Engine: exact/numerical calculation followed by verification."""

    _FUNCTIONS = {
        "sqrt": sp.sqrt,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "log": sp.log,
        "exp": sp.exp,
    }
    _CONSTANTS = {"pi": sp.pi, "E": sp.E}
    _MAX_AST_NODES = 200
    _MAX_INTEGER_BITS = 256

    def calculate(self, request: MathRequest) -> MathResult:
        expression = self._parse_expression(request.expression)
        substitutions = {}
        for name, value in request.variables.items():
            if not isinstance(name, str) or not name.isidentifier() or name.startswith("__"):
                raise ValueError(f"Invalid variable name: {name!r}")
            if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                raise ValueError(f"Variable {name!r} must be a finite number")
            substitutions[sp.Symbol(name)] = value
        evaluated = expression.subs(substitutions)
        exact = sp.simplify(evaluated)
        if exact.has(sp.zoo, sp.oo, -sp.oo, sp.nan):
            raise ValueError("Mathematical result is undefined or non-finite")

        if request.mode is MathMode.exact:
            result_text = sp.sstr(exact)
            verification = self._verify_exact(expression, exact, substitutions)
            return MathResult(
                question=request.question.strip(),
                expression=request.expression.strip(),
                mode=request.mode,
                result=result_text,
                exact_result=result_text,
                verification=verification,
            )

        numeric = float(sp.N(exact, 16))
        verification = self._verify_numerical(expression, exact, numeric, substitutions)
        return MathResult(
            question=request.question.strip(),
            expression=request.expression.strip(),
            mode=request.mode,
            result=repr(numeric),
            exact_result=sp.sstr(exact),
            numerical_result=numeric,
            verification=verification,
        )

    @classmethod
    def _parse_expression(cls, expression: str) -> sp.Expr:
        """Parse only a small mathematical grammar; never execute arbitrary Python."""
        try:
            tree = ast.parse(expression, mode="eval")
            if sum(1 for _ in ast.walk(tree)) > cls._MAX_AST_NODES:
                raise ValueError("Mathematical expression is too complex")
            return cls._convert(tree.body)
        except (SyntaxError, ValueError, TypeError) as exc:
            raise ValueError(f"Invalid mathematical expression: {expression}") from exc

    @classmethod
    def _convert(cls, node: ast.AST) -> sp.Expr:
        if isinstance(node, ast.Constant) and isinstance(node.value, int) and abs(node.value).bit_length() > cls._MAX_INTEGER_BITS:
            raise ValueError("Integer literal is too large")
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            if isinstance(node.value, float) and not math.isfinite(node.value):
                raise ValueError("Non-finite numeric literal is not allowed")
            return sp.Float(node.value) if isinstance(node.value, float) else sp.Integer(node.value)
        if isinstance(node, ast.Name):
            if node.id in cls._CONSTANTS:
                return cls._CONSTANTS[node.id]
            if node.id.isidentifier() and node.id not in cls._FUNCTIONS and not node.id.startswith("__"):
                return sp.Symbol(node.id)
            raise ValueError(f"Unsupported name: {node.id}")
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = cls._convert(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp):
            left = cls._convert(node.left)
            right = cls._convert(node.right)
            operations = {
                ast.Add: lambda: left + right,
                ast.Sub: lambda: left - right,
                ast.Mult: lambda: left * right,
                ast.Div: lambda: left / right,
                ast.Pow: lambda: left**right,
                ast.Mod: lambda: left % right,
            }
            if isinstance(node.op, ast.Pow) and isinstance(right, sp.Integer):
                if abs(int(right)) > 1000:
                    raise ValueError("Exponent is too large")
            for operation, builder in operations.items():
                if isinstance(node.op, operation):
                    try:
                        return builder()
                    except (ZeroDivisionError, ValueError, TypeError) as exc:
                        raise ValueError("Invalid mathematical operation") from exc
            raise ValueError("Unsupported mathematical operator")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            function = cls._FUNCTIONS.get(node.func.id)
            if function is None or node.keywords:
                raise ValueError(f"Unsupported mathematical function: {ast.unparse(node.func)}")
            if len(node.args) != 1:
                raise ValueError(f"Function {node.func.id} expects exactly one argument")
            return function(cls._convert(node.args[0]))
        raise ValueError(f"Unsupported mathematical syntax: {type(node).__name__}")

    @staticmethod
    def _verify_exact(
        original: sp.Expr, result: sp.Expr, substitutions: dict[sp.Symbol, float]
    ) -> VerificationResult:
        residual = sp.simplify(original.subs(substitutions) - result)
        verified = residual == 0
        return VerificationResult(
            verified=verified,
            method="SymPy symbolic residual check",
            details=f"Residual={sp.sstr(residual)}",
        )

    @staticmethod
    def _verify_numerical(
        original: sp.Expr,
        exact: sp.Expr,
        numeric: float,
        substitutions: dict[sp.Symbol, float],
    ) -> VerificationResult:
        if not np.isfinite(numeric):
            return VerificationResult(
                verified=False,
                method="NumPy finite-value check",
                details="Numerical result is not finite.",
            )
        reference = float(sp.N(exact, 16))
        residual = abs(numeric - reference)
        residual_norm = float(norm(np.asarray([residual], dtype=float)))
        tolerance = max(1e-12, 1e-10 * max(1.0, abs(reference)))
        verified = math.isfinite(residual_norm) and residual_norm <= tolerance
        return VerificationResult(
            verified=verified,
            method="SymPy evaluation + NumPy finite check + SciPy residual norm",
            details=f"Reference={reference}; residual={residual_norm}; tolerance={tolerance}",
        )
