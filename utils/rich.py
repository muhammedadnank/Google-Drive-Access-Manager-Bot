import logging
from typing import Any, List, Optional, Union
from pyrogram import Client, enums
from pyrogram.types import InputRichMessage

logger = logging.getLogger(__name__)

def format_time_tag(unix_timestamp: int, format_str: str = "wDT") -> str:
    """
    Formats a dynamic client-side relative/absolute timestamp tag for Telegram Rich Messages.
    
    Example output: '![expires](tg://time?unix=1770000000&format=wDT)'
    Formats:
    - 'wDT': Relative time + full date & time
    - 'r': Relative time (e.g. 'in 2 days', '5 minutes ago')
    - 'd': Date only
    - 't': Time only
    - 'F': Full date and time
    """
    return f"![time](tg://time?unix={unix_timestamp}&format={format_str})"

def format_table(
    headers: List[str],
    rows: List[List[Any]],
    alignment: Optional[List[str]] = None
) -> str:
    """
    Formats a Rich Markdown table string.
    
    :param headers: List of column header names (max 20 columns).
    :param rows: List of row data lists (max 100 rows).
    :param alignment: Optional list of alignment strings per column: 'left', 'center', 'right'.
    :return: Markdown formatted table string.
    """
    if not headers or not rows:
        return ""
    
    # Enforce limit: max 20 columns
    headers = headers[:20]
    
    # Build header row
    header_line = "| " + " | ".join(headers) + " |"
    
    # Build alignment row
    align_parts = []
    for i in range(len(headers)):
        align = alignment[i] if alignment and i < len(alignment) else "left"
        if align == "center":
            align_parts.append(":---:")
        elif align == "right":
            align_parts.append("---:")
        else:
            align_parts.append(":---")
    align_line = "|" + "|".join(align_parts) + "|"
    
    # Build data rows (max 100 rows)
    row_lines = []
    for row in rows[:100]:
        row_cells = [str(cell) for cell in row[:len(headers)]]
        row_lines.append("| " + " | ".join(row_cells) + " |")
        
    return "\n".join([header_line, align_line] + row_lines)

def format_accordion(title: str, body: str, is_open: bool = False) -> str:
    """
    Formats a collapsible details block (Accordion) containing Rich Markdown content.
    
    :param title: Summary title text (max 64 chars).
    :param body: Markdown content inside the accordion.
    :param is_open: Whether the accordion is open by default.
    """
    # Enforce title length limit: max 64 chars
    clean_title = title[:64]
    open_attr = " open" if is_open else ""
    return f"<details{open_attr}><summary>{clean_title}</summary>\n\n{body}\n\n</details>"

def format_task_list(tasks: List[tuple[str, bool]]) -> str:
    """
    Formats an interactive task list string.
    
    :param tasks: List of tuples (task_label, is_completed).
    """
    lines = []
    for label, completed in tasks:
        checkbox = "[x]" if completed else "[ ]"
        lines.append(f"- {checkbox} {label}")
    return "\n".join(lines)

async def send_rich_or_text(
    target_or_client: Any,
    markdown_content: str,
    reply_markup: Any = None,
    chat_id: Optional[Union[int, str]] = None,
    receiver_user_id: Optional[int] = None
) -> Any:
    """
    Attempts to send a Rich Message via Markdown, with seamless fallback to standard Markdown on error.
    Accepts either (client, text, reply_markup, chat_id, receiver_user_id) or (message/callback_query, text, ...).
    """
    try:
        if isinstance(target_or_client, Client):
            client = target_or_client
            target_chat_id = chat_id
        else:
            client = getattr(target_or_client, "_client", None) or getattr(target_or_client, "client", None)
            if hasattr(target_or_client, "chat") and target_or_client.chat:
                target_chat_id = target_or_client.chat.id
            elif hasattr(target_or_client, "message") and target_or_client.message and target_or_client.message.chat:
                target_chat_id = target_or_client.message.chat.id
            else:
                target_chat_id = chat_id

        if client and hasattr(client, "send_rich_message"):
            kwargs = {
                "chat_id": target_chat_id,
                "rich_text": markdown_content,
                "parse_mode": enums.ParseMode.MARKDOWN,
                "reply_markup": reply_markup
            }
            return await client.send_rich_message(**kwargs)
        elif hasattr(target_or_client, "reply_text"):
            return await target_or_client.reply_text(
                text=markdown_content,
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            return await client.send_message(
                chat_id=target_chat_id,
                text=markdown_content,
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    except Exception as exc:
        logger.warning(f"send_rich_message failed ({exc}), falling back to standard send.")
        try:
            if hasattr(target_or_client, "reply_text"):
                return await target_or_client.reply_text(
                    text=markdown_content,
                    parse_mode=enums.ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            elif isinstance(target_or_client, Client):
                return await target_or_client.send_message(
                    chat_id=chat_id,
                    text=markdown_content,
                    parse_mode=enums.ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            elif client and target_chat_id:
                return await client.send_message(
                    chat_id=target_chat_id,
                    text=markdown_content,
                    parse_mode=enums.ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
        except Exception as fallback_exc:
            logger.error(f"Fallback send_message failed: {fallback_exc}")
            raise

async def edit_rich_or_text(
    target_or_client: Any,
    markdown_content: str,
    reply_markup: Any = None,
    chat_id: Optional[Union[int, str]] = None,
    message_id: Optional[int] = None
) -> Any:
    """
    Attempts to edit a Rich Message via Markdown, with seamless fallback to standard Markdown edit on error.
    Accepts either (client, text, reply_markup, chat_id, message_id) or (callback_query/message, text, reply_markup).
    """
    try:
        if isinstance(target_or_client, Client):
            client = target_or_client
            t_chat_id = chat_id
            t_message_id = message_id
        else:
            client = getattr(target_or_client, "_client", None) or getattr(target_or_client, "client", None)
            
            if chat_id is not None:
                t_chat_id = chat_id
            elif hasattr(target_or_client, "chat") and target_or_client.chat:
                t_chat_id = target_or_client.chat.id
            elif hasattr(target_or_client, "message") and target_or_client.message and target_or_client.message.chat:
                t_chat_id = target_or_client.message.chat.id
            else:
                t_chat_id = None
                
            if message_id is not None:
                t_message_id = message_id
            elif hasattr(target_or_client, "id"):
                t_message_id = target_or_client.id
            elif hasattr(target_or_client, "message") and target_or_client.message:
                t_message_id = target_or_client.message.id
            else:
                t_message_id = None

        if client and t_chat_id and t_message_id and hasattr(client, "edit_message_text"):
            return await client.edit_message_text(
                chat_id=t_chat_id,
                message_id=t_message_id,
                rich_text=markdown_content,
                rich_text_parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        elif hasattr(target_or_client, "edit_message_text"):
            return await target_or_client.edit_message_text(
                text=markdown_content,
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        elif hasattr(target_or_client, "edit_text"):
            return await target_or_client.edit_text(
                text=markdown_content,
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    except Exception as exc:
        if "MESSAGE_NOT_MODIFIED" in str(exc):
            return None
        logger.warning(f"edit_rich_or_text failed ({exc}), falling back to standard edit.")
        try:
            if isinstance(target_or_client, Client):
                return await target_or_client.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=markdown_content,
                    parse_mode=enums.ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            elif hasattr(target_or_client, "edit_message_text"):
                return await target_or_client.edit_message_text(
                    text=markdown_content,
                    parse_mode=enums.ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            elif hasattr(target_or_client, "edit_text"):
                return await target_or_client.edit_text(
                    text=markdown_content,
                    parse_mode=enums.ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
        except Exception as fallback_exc:
            if "MESSAGE_NOT_MODIFIED" not in str(fallback_exc):
                raise


