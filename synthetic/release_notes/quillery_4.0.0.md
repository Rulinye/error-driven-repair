# quillery 4.0.0 (August 2026)

## Backwards-incompatible changes

- `slugify` was renamed to `to_handle` (#88).
- `word_count` was removed. The counts of a text are now available from `digest(text)`, whose `words` attribute replaces it (#91).
- `Tokenizer.words` is now `Tokenizer.scan` (#95).
- `wrap` no longer accepts `width`; the line length is now given as `measure` (#97).
- The `strip_accents` argument of `normalize` was replaced by `fold`; `fold="ascii"` removes accents (#102).

## Other changes

- `title_case` keeps short function words such as "of" and "the" in lower case unless they come first (#79).
- `truncate` now counts the ellipsis within `limit` (#84).
- New function `dedent_block` removes the common indentation of a block of text (#99).
