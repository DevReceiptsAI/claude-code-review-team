# Production checklist (faceless: AI voice + rendered animation)

This channel does not film a face or a live screen, so this replaces the "recording" checklist. If you add real terminal footage, use the terminal section.

## Before rendering
- [ ] Full eval and hook test finished, scored, and written into METRICS.md (no `TODO: measure` left in anything that appears on screen)
- [ ] (Optional, not done yet) manual review of unmatched findings (eval/manual_verdicts.json); until then the video says they are "listed in the repo for review"
- [ ] Narration script updated for the real numbers, then `video/.venv/bin/python narration.py af_heart`
- [ ] Listen to the whole narration once; re-write any line that sounds off
- [ ] Render: `manim -r 2560,1440 --fps 30 scenes.py ArchitectureScene`, then `mix_sfx.py`, then mux with ffmpeg (see NOTES.md)
- [ ] Decide: sound effects on or off; background music or none (YouTube Audio Library, 10-20 dB under the voice, keep the licence record)

## Watch-through checks
- [ ] Nothing on screen held still for more than about 3-4 seconds without movement
- [ ] Every number on screen matches METRICS.md
- [ ] No text cut off at the edges, none overlapping the progress bar or footer
- [ ] Captions: upload `DevReceipts-Video1-DRAFT.srt` as normal captions (do not burn in)

## If you show a real terminal (replays of the actual runs)
- Font size large (about 20-24 pt), dark theme, window sized to 16:9
- Windows to open: only the terminal; close mail, chat, Finder
- Commands to run in order: `make test`, `make eval`, `python3 eval/score.py`
- Never show: API keys or `.env`, your username or home path if avoidable, the Downloads folder (it holds personal documents), account emails, usage/billing screens

## Upload
- [ ] Title, thumbnail and hook make the same promise
- [ ] AI-voice disclosure set the way YouTube's current guidance asks (check Studio)
- [ ] Description filled in, repo link live, chapters added
- [ ] Playlist "Agents: Real Builds"
- [ ] Watermark set to the entire video
