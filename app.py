import json
import os
import string
from urllib.parse import quote_plus

from flask import Flask, jsonify, redirect, request


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_PATH = os.path.join(BASE_DIR, "rules.json")


app = Flask(__name__)


RULES = {}
ESCAPE_KEYWORD = "nofind"
DEFAULT_SEARCH = "https://www.google.com/search?q={q}"


def load_rules():
    """Load rules.json into memory, falling back to safe defaults on error."""
    global RULES, ESCAPE_KEYWORD, DEFAULT_SEARCH

    RULES = {}
    ESCAPE_KEYWORD = "nofind"
    DEFAULT_SEARCH = "https://www.google.com/search?q={q}"

    try:
        with open(RULES_PATH, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError, ValueError):
        return

    if not isinstance(payload, dict):
        return

    escape_keyword = payload.get("escape_keyword")
    default_search = payload.get("default_search")
    rules = payload.get("rules")

    if isinstance(escape_keyword, str) and escape_keyword:
        ESCAPE_KEYWORD = escape_keyword

    if isinstance(default_search, str) and default_search:
        DEFAULT_SEARCH = default_search

    if isinstance(rules, dict):
        RULES = rules


def build_default_search_url(query):
    return DEFAULT_SEARCH.replace("{q}", quote_plus(query))


def build_rule_url(rule, args):
    rule_type = rule.get("type")
    join_args = rule.get("join_args", False)

    if rule_type == "static":
        url = rule.get("url")
        if not isinstance(url, str) or not url:
            raise ValueError("Invalid static rule")
        return url

    if rule_type == "template":
        template = rule.get("template")
        arg_defaults = rule.get("arg_defaults", [])

        if not isinstance(template, str) or not template:
            raise ValueError("Invalid template rule")
        if not isinstance(arg_defaults, list):
            raise ValueError("Invalid arg_defaults")
        if not isinstance(join_args, bool):
            raise ValueError("Invalid join_args")

        if join_args:
            args = [quote_plus(" ".join(args))]

        formatter = string.Formatter()
        max_index = -1
        for _, field_name, _, _ in formatter.parse(template):
            if field_name is None or field_name == "":
                continue
            try:
                max_index = max(max_index, int(field_name))
            except ValueError as exc:
                raise ValueError("Template placeholders must be numeric") from exc

        value_count = max(max_index + 1, len(args), len(arg_defaults))
        values = []
        for index in range(value_count):
            if index < len(args):
                values.append(args[index])
            elif index < len(arg_defaults):
                values.append(arg_defaults[index])
            else:
                values.append("")

        return template.format(*values)

    raise ValueError("Unknown rule type")


def redirect_default(query):
    return redirect(build_default_search_url(query), code=302)


load_rules()


@app.get("/go")
def go():
    q = request.args.get("q", "")
    if not q:
        return redirect_default("")

    parts = q.split(maxsplit=1)
    keyword = parts[0]
    rest = parts[1] if len(parts) > 1 else ""

    if keyword == ESCAPE_KEYWORD:
        return redirect_default(rest)

    rule = RULES.get(keyword)
    if isinstance(rule, dict):
        try:
            target_url = build_rule_url(rule, rest.split())
            return redirect(target_url, code=302)
        except Exception:
            return redirect_default(q)

    return redirect_default(q)


@app.get("/reload")
def reload_rules():
    load_rules()
    return jsonify(
        {
            "ok": True,
            "escape_keyword": ESCAPE_KEYWORD,
            "rule_count": len(RULES),
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
