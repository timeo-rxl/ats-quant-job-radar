<!-- LOVABLE:BEGIN -->
> [!IMPORTANT]
> This project is connected to [Lovable](https://lovable.dev). Avoid rewriting
> published git history — force pushing, or rebasing/amending/squashing commits
> that are already pushed — as it rewrites history on Lovable's side and the
> user will likely lose their project history.
>
> Commits you push to the connected branch sync back to Lovable and show up in
> the editor, so keep the branch in a working state.

## What Lovable manages

Rules outside this block are the project's own. Change the pieces below in
Lovable, not by hand. With the [Lovable MCP](https://mcp.lovable.dev)
connected, `send_message` asks Lovable to do it; otherwise ask the user to
use the editor.

- **Database.** Do not add or edit `supabase/migrations/` or `drizzle/`.
  Ask Lovable to change the schema.
- **Generated files.** Do not edit a file whose header says it is automatically
  generated.
- **AI gateway.** Keep model calls on Lovable's gateway, and keep
  `LOVABLE_API_KEY` out of browser code.
- **Connectors.** Lovable provides native connectors. `list_connectors` shows
  which are enabled; `add_connector` only returns the dashboard link. When a
  connector is enabled, calls go through the connector gateway and need
  `LOVABLE_API_KEY`. When Lovable does not provide one, users can bring their
  own key and store it in Secrets.
- **Secrets.** Lovable manages them. Do not put secret values in the repo.
<!-- LOVABLE:END -->

## Project rules
- No backend: profile, language and tracker live in localStorage via `src/lib/store.ts` (useSyncExternalStore) — keeps the app account-free and SSR-safe.
- All UI text goes through `src/lib/i18n.ts` (FR/EN dict); program data in `src/data/programs.json` is the single source of truth.
- Matching logic lives only in `src/lib/matching.ts`, covered by `src/lib/matching.test.ts`.
- Graduation input uses a typed year-month value with a localized Shadcn calendar; this avoids browser-locale-dependent native month labels.
- Result views share ResetProfile so restoring defaults changes only the profile, not language, filters or tracker.
- LogoStrip warms the shared logo sources on mount and clamps rotated card bounds; Logo shows initials until an image is ready to avoid empty or broken cards.
