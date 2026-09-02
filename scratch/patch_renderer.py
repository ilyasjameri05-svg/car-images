import re

with open("scratch/answer_key_logic.py", "r", encoding="utf-8") as f:
    code = f.read()

replacement = ""
# get the string inside get_answer_key_logic():
start_idx = code.find("'''\n") + 4
end_idx = code.rfind("'''")
replacement = code[start_idx:end_idx]

with open("app/pdf/page_renderer.py", "r", encoding="utf-8") as f:
    orig = f.read()

# We want to replace from `def render_answer_key_page` up to `def render_title_page`
start_marker = "    def render_answer_key_page("
end_marker = "    # ======================================================================\n    # Title / Intro pages"

s_idx = orig.find(start_marker)
e_idx = orig.find(end_marker)

if s_idx != -1 and e_idx != -1:
    new_orig = orig[:s_idx] + replacement + "\n" + orig[e_idx:]
    with open("app/pdf/page_renderer.py", "w", encoding="utf-8") as f:
        f.write(new_orig)
    print("Replaced successfully.")
else:
    print(f"Could not find markers. s_idx={s_idx}, e_idx={e_idx}")
