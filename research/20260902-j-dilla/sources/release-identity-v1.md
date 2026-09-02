# J Dilla clock-relation corpus: release identity v1

## Evidence boundary

This ledger fixes catalog candidates before audio measurement. It does not assert that catalog entries are waveform-identical, and it does not claim that any full-length audio has been acquired. A playable preview, a title match, or a catalog duration is not a file identity.

## Decisions

| Recording ID | Current decision | Catalog evidence | Published analysis anchor | Remaining gate |
| --- | --- | --- | --- | --- |
| `runnin-analysis-master` | Use the original `Labcabincalifornia` catalog entry as the candidate | Apple Music identifies the album as 1995 and exposes separate Deluxe and 30th Anniversary editions | Peterson Figures 14-15: 4:32-4:37 | Acquire a lawful source, hash it, and confirm that the anchor aligns |
| `players-analysis-master` | **Ambiguous** between `Fan-Tas-Tic Vol. 1` and `Fantastic Vol. 2` | The catalogs expose materially different entries/durations under the same title | Peterson Figure 16: 2:13-2:19, a four-measure kick loop | Compare the anchor content or fingerprints; title and duration alone are insufficient |
| `keep-it-on-this-beat-analysis-master` | Use `Fan-Tas-Tic Vol. 1` track 2 as the candidate | Track lists distinguish track 2 `Keep It On (This Beat)` from track 14 `Keep It On` / remix | Peterson Figure 17: 0:57-1:01 | Acquire, hash, and confirm track/anchor alignment |
| four `come-get-it-*` IDs | Use tracks 5, 21, 44, and 45 of the official 2021 anniversary collection as four named candidates | Official J Dilla Bandcamp lists 5:02, 4:25, 4:05, and 1:26 respectively | Peterson Figures 20-21: 0:08-0:18 for the 2001 track | Verify the album candidate against the published anchor, then locate homologous 16-bar regions in each variant |

## Primary and distributor sources

- Sean Peterson, *Something Real: Rap, Resistance, and the Music of the Soulquarians* (University of Oregon, 2018): https://scholarsbank.uoregon.edu/items/5b4c64fb-52b8-4c19-82fd-7289be624d66/full
- Dissertation bitstream used for figure times and descriptions: https://scholarsbank.uoregon.edu/bitstreams/0e04faef-6878-4733-92d0-ae4cf00f9ecd/download
- The Pharcyde, `Runnin'`, original-album Apple Music entry: https://music.apple.com/us/song/runnin/1440915343
- The Pharcyde, `Labcabincalifornia`, Apple Music album entry: https://music.apple.com/us/album/labcabincalifornia/1440914966
- Slum Village, `Fan-Tas-Tic Vol. 1`, Spotify album entry: https://open.spotify.com/album/78xn7eWk5Q5MiEqtetsNer
- Slum Village, `Fantastic Vol. 2`, Spotify album entry: https://open.spotify.com/album/3nwgfMl8nYGTNqiepnoEFY
- J Dilla / BBE Music, `Welcome 2 Detroit - The 20th Anniversary Edition`: https://jdilla.bandcamp.com/album/welcome-2-detroit-the-20th-anniversary-edition

## Non-equivalence rules

1. Catalog duration belongs in `catalog_duration_seconds`; it must never populate the file-derived `duration_seconds` field.
2. `source_locator` remains null until the exact acquired bytes and rights basis are recorded. A catalog page belongs under `catalog_candidates[].locator`.
3. `reference_intervals` are published examples, not automatically the future 16-bar experimental regions.
4. An `ambiguous` identity cannot become `ready`; acquisition alone does not resolve version identity.
5. Remasters, deluxe editions, instrumentals, demos, alternate beats, and remixes remain distinct until hash or content alignment justifies equivalence.
