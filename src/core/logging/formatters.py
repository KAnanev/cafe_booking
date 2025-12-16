"""Форматтеры для логирования."""


def create_log_format(
    include_module: bool = True,
    include_function: bool = True,
    include_line: bool = True,
    include_traceback: bool = True,
) -> str:
    """Создает формат строки лога для loguru."""
    time_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} {time:ZZ}"
    parts = [
        time_format,
        "|",
        "{level: <8}",
        "|",
        "{extra[user_info]:-<20}",
        "|",
        "{message}",
    ]
    extra_parts = []
    if include_module:
        extra_parts.append("module={name}")
    if include_function:
        extra_parts.append("function={function}")
    if include_line:
        extra_parts.append("line={line}")
    if extra_parts:
        parts.append("|")
        parts.append(" ".join(extra_parts))
    parts.append("| {extra[event_details]}")
    if include_traceback:
        parts.append("\n{exception}")
    return " ".join(parts)
