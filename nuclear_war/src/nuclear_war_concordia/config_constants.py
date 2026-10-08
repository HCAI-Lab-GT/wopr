"""Constants for Concordia no-press harness config parsing."""

AGENTS = {
    "concordia_first_legal",
    "concordia_http",
    "concordia_native_first_legal",
    "concordia_native_http",
    "concordia_scripted",
}
HTTP_AGENTS = {"concordia_http", "concordia_native_http"}
AUTHORITY_AGENTS = {"concordia_first_legal", "concordia_http"}
NATIVE_AGENTS = {"concordia_native_first_legal", "concordia_native_http"}
RUNTIMES = {"auto", "concordia_runtime", "concordia_style_fallback"}
PRESS_MODES = {"none", "press_light", "multi_turn_public", "full_press"}
