"""Lab 2, Step 2: the agent's actuators.

calculator  - safe arithmetic with the ast module (never eval)
wiki_lookup - Wikipedia page summary via the free REST endpoint
"""
import ast
import operator as op

import requests

OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
       ast.Div: op.truediv, ast.USub: op.neg}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Unsupported expression")


def calculator(expression: str) -> str:
    try:
        expr = expression.replace(",", "").strip().strip("`")
        result = _eval(ast.parse(expr, mode="eval").body)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return str(result)
    except Exception as e:
        return f"Error: {e}"


def wiki_lookup(title: str) -> str:
    url = ("https://en.wikipedia.org/api/rest_v1/page/summary/"
           + title.strip().strip('"').replace(" ", "_"))
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "DCIT403-lab"})
    except requests.RequestException as e:
        return f"Error: could not reach Wikipedia ({e.__class__.__name__})."
    if r.status_code != 200:
        return f"No Wikipedia page found for '{title}'."
    return r.json().get("extract", "")[:800]


TOOLS = {"calculator": calculator, "wiki_lookup": wiki_lookup}


if __name__ == "__main__":
    # Step 2 checkpoint: test both tools directly.
    print("calculator('4*185 + 3*95')       ->", calculator("4*185 + 3*95"))
    print("calculator('1,200 - 1025')       ->", calculator("1,200 - 1025"))
    print("calculator(\"__import__('os')\") ->", calculator("__import__('os')"))
    print("calculator('2**1000000')         ->", calculator("2**1000000"))
    print("wiki_lookup('Bono East Region')  ->", wiki_lookup("Bono East Region")[:200], "...")
    print("wiki_lookup('Xyzzy Nonexistent Page 403') ->", wiki_lookup("Xyzzy Nonexistent Page 403"))
