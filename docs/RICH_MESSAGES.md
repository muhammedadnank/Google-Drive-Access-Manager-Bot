# 🎨 Telegram Bot API 10.1 & 10.2 (Kurigram / Pyrogram Layer 228+) Rich Markdown Specification & Guide

Comprehensive guide for integrating **Telegram Bot API 10.1 / 10.2 & Kurigram/Pyrogram Layer 228+ Rich Message System (Markdown Focus)** into Telegram Bot and Userbot projects.

---

## 📌 1. Overview & Architecture

The **Rich Message Engine** (introduced in Telegram Bot API 10.1 and enhanced in 10.2) allows bots to send rich, structured documents using native **Rich Markdown** (`InputRichMessage(markdown=...)`).

With **Rich Markdown**, bots can render:
- 📊 **Structured Data Tables** with column alignment (Left, Center, Right).
- 📁 **Collapsible Accordions (`<details>`)** containing rich nested Markdown content.
- 📋 **Task Lists (`- [ ]`, `- [x]`)** and multi-level ordered/unordered lists.
- ⏱️ **Live Dynamic Timestamps** (`![label](tg://time?unix=...&format=...)`).
- 🖼️ **Inline Media Blocks**, **Media Collages (`<tg-collage>`)**, and **Slideshows (`<tg-slideshow>`)**.
- 🧮 **TeX Math Equations** (`$$E = mc^2$$`), **Footnotes (`[^id]`)**, **Subscript/Superscript**, **Marked Text (`==text==`)**, and **Spoilers (`||spoiler||`)**.
- 🔒 **Ephemeral Group Responses** (`receiver_user_id`) for private data delivery in public groups.

---

## ⚙️ 2. Official Telegram Bot API Specifications & Limits

> [!IMPORTANT]
> Always enforce these system limits to prevent `400 BAD_REQUEST` Telegram API errors:

| Parameter / Feature | Operational Limit | Notes / Requirements |
| :--- | :--- | :--- |
| **Max Message Length** | `32,768` characters | Total raw markup characters across all blocks. |
| **Max Structural Blocks** | `500` blocks | Total nested/top-level block count per message. |
| **Data Tables (`| header |`)**| Max `20` columns, Max `100` rows | Cell contents support inline formatting (bold, code, links). |
| **Accordions (`<details>`)**| Max Summary Title: `64` chars; Max Depth: `3` | `<summary>` tag holds accordion header text. |
| **Thinking Blocks (`<tg-thinking>`)** | Max `4,096` chars | Used for AI generation / API processing states. |
| **Media Attachments** | Max `10` files per rich message | Attached via `![](url)` media syntax or `InputRichMessageMedia`. |
| **Entity Detection** | Optional (`skip_entity_detection=True`) | Disables automatic URL/email/cashtag detection. |

---

## 📝 3. Comprehensive Rich Markdown Syntax Reference

### A. Inline Formatting & Interactive Elements

```markdown
**bold text** or __bold text__
*italic text* or _italic text_
~~strikethrough text~~
`inline fixed-width code`
==marked text==
||spoiler||

[inline URL](https://t.me/)
[inline e-mail](mailto:user@example.com)
[inline phone number](tel:+123456789)
[inline mention of a user](tg://user?id=123456789)

![👍](tg://emoji?id=5368324170671202286)
![22:45 tomorrow](tg://time?unix=1647531900&format=wDT)

$x^2 + y^2$
\#hashtag $USD +12345678901, card: 4242 4242 4242 4242, https://t.me t.me a@t.me /command @username
```

| Syntax | Output / Render Description |
| :--- | :--- |
| `**bold**` / `__bold__` | **Bold text** |
| `*italic*` / `_italic_` | *Italic text* |
| `~~strikethrough~~` | ~Strikethrough text~ |
| `` `code` `` | `inline monospace code` |
| `==marked text==` | Highlighted / Marked text background |
| `||spoiler||` | Blurred spoiler effect |
| `[Label](url)` | Hyperlink |
| `![emoji](tg://emoji?id=...)` | Custom Telegram Animated Emoji |
| `![time](tg://time?unix=...&format=...)` | Client-rendered dynamic timestamp |
| `$x^2 + y^2$` | Inline TeX Mathematical expression |

---

### B. Headings, Preformatted Code & Quotations

```markdown
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6

Paragraph text

```python
def fetch_access_token():
    print("Pre-formatted fixed-width code block")
```

---

> Block quotation started
>
> Block quotation continued on the next line
> The last line of the block quotation
```

---

### C. Lists & Task Lists

```markdown
- Unordered list item
* Unordered list item
+ Unordered list item

1. Ordered list item
2. Ordered list item

- [ ] Pending task list item
- [x] Completed task list item
```

---

### D. Data Tables (With Column Alignment)

```markdown
| Metric | Value | Status |
|:-------|:-----:|-------:|
| Speed  | **42** <sup>ms</sup> | 🟢 Active |
| Storage| `1.2 GB` | ||Encrypted|| |
```

---

### E. Footnotes & TeX Math Blocks

```markdown
Text with a reference[^id1] and another one[^id2].

[^id1]: Definition of the first footnote.
[^id2]: Definition of the second footnote.

$$E = mc^2$$

```math
E = mc^2
```
```

---

### F. Media Blocks, Collages & Slideshows

```markdown
<!-- Standalone Media Blocks with Captions -->
![](https://telegram.org/example/photo.jpg "Photo caption")
![](https://telegram.org/example/video.mp4 "Video caption")
![](https://telegram.org/example/audio.mp3 "Audio caption")
![](https://telegram.org/example/audio.ogg "Voice note caption")
![](https://telegram.org/example/animation.gif "Animation caption")

<!-- Grid Collage of Media -->
<tg-collage>
![](https://telegram.org/example/photo.jpg)
![](https://telegram.org/example/video.mp4)
</tg-collage>

<!-- Swipeable Media Slideshow -->
<tg-slideshow>
![](https://telegram.org/example/photo.jpg)
![](https://telegram.org/example/video.mp4)
</tg-slideshow>
```

---

### G. Collapsible Details Blocks (Accordions)

```markdown
<details open><summary>Summary with **bold text**</summary>

### Details heading
- List item with _italic text_
- List item with ||spoiler||

</details>
```

---

### H. Advanced Nested Markdown & HTML Hybrid Syntax

```markdown
## Example Nested Syntax Report for _Q1_
Intro with <u>underlined text</u>, ==marked text==, and $x^2 + y^2$.
**Bold _italic <u>underlined italic bold</u> italic_ bold**
<u>In inline tags, nested **markdown** is parsed</u>

> Quote with **bold text, ~~strikethrough, and <tg-spoiler>spoiler</tg-spoiler>~~**, plus [a link](https://t.me/).

- List item with `code`, <sup>superscript</sup>, <sub>subscript</sub>, and a footnote[^note]
- Another item with **bold <tg-spoiler><code>spoiler code</code></tg-spoiler>**
- Another item with ~~strikethrough and <ins>inserted text</ins>~~

[^note]: Footnote with _italic text_ and <u>HTML underline</u>.
```

---

## 🏷️ 4. Rich HTML Reference (Alternative Syntax)

For reference, Telegram also supports explicit Rich HTML mode via `InputRichMessage(html=...)`:

```html
<h1>Header</h1>
<p>Paragraph</p>
<details><summary>Summary</summary>Content</details>
<table><tr><th>Col</th></tr><tr><td>Val</td></tr></table>
```

---

## 🚀 5. Kurigram / Pyrogram Code Setup & Usage

### 📦 Essential Imports

```python
from pyrogram import Client
from pyrogram.types import (
    InputRichMessage,
    InputRichMessageMedia,
    RichBlockSectionHeading,
    RichBlockParagraph,
    RichBlockTable,
    RichBlockTableCell,
    RichBlockDivider,
    RichBlockFooter,
    RichBlockDetails,
)
```

### 📩 Sending Rich Messages (Markdown Mode)

```python
# Sending Rich Markdown Message
await app.send_rich_message(
    chat_id=chat_id,
    rich_text="""
# 📊 System Overview

| Metric | Count | Status |
|:-------|:-----:|-------:|
| Active Users | **150** | 🟢 Healthy |
| Pending Jobs | **3** | 🟡 Processing |

<details><summary>📂 View Details</summary>

- [x] Sync Google Drive API
- [ ] Clean expired tokens
- [ ] Export database backup

</details>

---
_Generated by Google Drive Access Manager Bot_
    """,
    parse_mode=enums.ParseMode.MARKDOWN,
    reply_markup=reply_markup
)
```

### 🔒 Ephemeral Group Messages — *Bot API 10.2 Concept*

> [!TIP]
> Use rich message formatting in group chats so sensitive access information (like email addresses) is neatly structured!

```python
await app.send_rich_message(
    chat_id=group_chat_id,
    rich_text="""
🔒 **Private Access Credentials**
- User Email: `user@domain.com`
- Permission: ==Editor Access==
    """,
    parse_mode=enums.ParseMode.MARKDOWN
)
```

---

## 🛡️ 6. Production Safe Fallback Helper

```python
import logging
from pyrogram import Client, enums

logger = logging.getLogger(__name__)

async def send_rich_or_text(
    client: Client,
    chat_id: int | str,
    markdown_content: str,
    reply_markup=None
):
    """
    Attempts to send a Rich Message via Markdown, with seamless fallback to standard Markdown text.
    """
    try:
        return await client.send_rich_message(
            chat_id=chat_id,
            rich_text=markdown_content,
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    except Exception as exc:
        logger.warning(f"Rich message send failed ({exc}), falling back to standard text.")
        return await client.send_message(
            chat_id=chat_id,
            text=markdown_content,
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

async def edit_rich_or_text(
    client: Client,
    chat_id: int | str,
    message_id: int,
    markdown_content: str,
    reply_markup=None
):
    """
    Attempts to edit a Rich Message via Markdown, with seamless fallback to standard Markdown text.
    """
    try:
        return await client.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            rich_text=markdown_content,
            rich_text_parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    except Exception as exc:
        logger.warning(f"Rich message edit failed ({exc}), falling back to standard text.")
        return await client.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=markdown_content,
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
```

---

## 🎯 7. Google Drive Access Manager Bot Implementation Blueprint

### A. Analytics & System Stats (`plugins/analytics.py`)
```python
md_stats = f"""
# 📊 Storage & Access Analytics

| Metric | Count | Status |
|:-------|:-----:|-------:|
| Active Grants | **{active_grants}** | 🟢 Healthy |
| Expired Access| **{expired_grants}** | 🔴 Cleaned |
| Total Folders | **{total_folders}** | 📁 Synced |

---
_Auto-refreshed via Google Drive Access Manager_
"""
```

### B. Access Expiry Tracking (`plugins/expiry.py`)
```python
md_expiry = f"""
# ⏱️ Access Expiry Status

- User: `user@gmail.com`
- Folder: **Project Backup**
- Expires: ![expires](tg://time?unix={expiry_timestamp}&format=wDT)

- [x] Granted permission
- [ ] Expired & revoked
"""
```

### C. Search & Multi-Folder Manager (`plugins/search.py`)
```python
md_folders = f"""
# 📁 Managed Drive Folders

<details open><summary>📂 Project Alpha (3 Users)</summary>

- alex@gmail.com — _Editor_
- john@gmail.com — _Viewer_

</details>

<details><summary>📂 Backup Vault (1 User)</summary>

- admin@company.com — _Owner_

</details>

---
_Select an option below to modify access_
"""
```

---

## 📚 8. Summary Checklist for Developers

- [x] Use `InputRichMessage(markdown=...)` as primary mode for structured messaging.
- [x] Use Markdown Tables (`| Header 1 | Header 2 |`) for analytics and stats dashboards.
- [x] Use Accordions (`<details><summary>Title</summary>...</details>`) for multi-folder listings.
- [x] Use Task Lists (`- [ ]`, `- [x]`) for status workflows.
- [x] Use `![label](tg://time?unix=...&format=...)` for client-rendered expiration countdowns.
- [x] Use `receiver_user_id` in groups for privacy.
