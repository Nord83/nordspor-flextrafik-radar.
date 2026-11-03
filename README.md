# Nordspor Flextrafik Radar – automatisk kildeovervågning

Denne version bygger videre på det oprindelige Nordspor-dashboard. Den overvåger **offentligt synlige links** på 10 officielle indgangssider med GitHub Actions, ca. hver time. **Det er ikke en officiel API-integration eller kontinuerlig realtid.**

## Få radaren online – trin for trin

1. Opret en gratis GitHub-konto på https://github.com og opret et **nyt public repository** med navnet `nordspor-flextrafik-radar` (ingen README ved oprettelsen).
2. Pak ZIP-filen ud. Vælg **Add file → Upload files** i repositoryet og upload **indholdet** af mappen, inklusive `.github/workflows/radar.yml` (skjulte mapper kan være svære at se i visse filvælgere). Alternativt brug GitHub Desktop til at kopiere og pushe hele mappen.
3. Åbn **Settings → Pages → Build and deployment → Deploy from a branch**. Vælg `main` og `/ (root)`, og tryk **Save**.
4. Åbn **Actions → Opdater Nordspor Radar → Run workflow**. Under **Settings → Actions → General → Workflow permissions** vælg **Read and write permissions**, hvis workflowet ikke må pushe data. GitHub kan også kræve, at Actions aktiveres.
5. Efter et vellykket workflow og Pages-deploy: åbn `https://DIT-BRUGERNAVN.github.io/nordspor-flextrafik-radar/`.
6. Kontrollér panelet **Live kildeovervågning**. Kilder med fejl markeres eksplicit. Genindlæs siden for at se nye data.

## Hvad overvåges?

- Midttrafik (to sider), Sydtrafik, FynBus, NT, Movia, udbud.dk, TED, Færdselsstyrelsen og Trafikselskaberne i Danmarks omkostningsindeks.
- Nye links med relevante nøgleord registreres i `data/events.json` efter en vellykket baseline-kørsel.
- Sidste kontrol, sidste succes og fejl pr. kilde vises i `data/radar.json`.
- Eksisterende udbud, regler og frister i det oprindelige dashboard er **historisk baseline fra 2. november 2026**, ikke automatisk verificerede oplysninger.

## Vigtige begrænsninger

- Nye links er **ikke automatisk et nyt udbud**. Et nyt tilbud, ændret frist, annullering, adgangskrav eller prisregulering kræver manuel kontrol af **det konkrete officielle udbudsmateriale**.
- Dette er **ikke en komplet udbud.dk/TED/Ethics-indeksering**. JavaScript-tunge sider, login, botbeskyttelse og dybe dokumentlinks kan ikke altid aflæses. Der er ingen automatisk PDF- eller bilagsanalyse.
- Et uændret link kan have fået ændret indhold, uden at det registreres. Slettede links registreres ikke som annulleringer.
- GitHub Actions cron er best-effort og kan blive forsinket eller sat på pause ved inaktivitet. Fejl i en kilde vises; de må ikke fortolkes som ingen nyheder.
- Ingen e-mail/SMS/push er konfigureret. Notifikationer kræver separat integration. Brug kun verificerede kilder til frister.
- GitHub Pages i et public repository er offentligt tilgængeligt. Gem **ikke** fortrolige oplysninger, API-nøgler eller persondata i repositoryet.
- Data gemmes i repositoryets git-historik. Browsernoter forbliver lokale i browseren.

## Test lokalt

```bash
python -m pip install -r requirements.txt
python scripts/update.py
python -m http.server 8000
```

Åbn `http://localhost:8000/`. En lokal `file://`-visning understøtter ikke nødvendigvis `fetch()` af JSON.

## Næste tekniske udvidelse

For produktionsklar overvågning bør man tilføje officielle API'er eller tilladte feeds, præcise opslag i Ethics og TED, dokument-download og versionsdiff, fristparser med kildebevis, manuel godkendelse og e-mailalarm kun ved verificerede væsentlige ændringer. Særligt FV10 bør have en dedikeret overvågning af det konkrete udbuds-ID, når det offentliggøres.
