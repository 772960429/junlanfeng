# Junlan Feng - Personal Website (Sharon Li Style)

Clean, academic-style personal website inspired by [Sharon Li](https://pages.cs.wisc.edu/~sharonli/).

## Structure

```
.
├── index.html              # About page
├── publications.html       # Publications & Patents
├── experience.html         # Work Experience & Projects
├── awards.html             # Awards & Leadership
├── style.css               # All styles (single file)
├── app.js                  # Data loading & rendering
├── data/
│   └── profile.json        # All content data
└── README.md
```

## Deploy to GitHub Pages

1. Create a new GitHub repository
2. Upload all files in this folder to the repo root
3. Go to **Settings → Pages**
4. Source: Deploy from a branch → select `main` branch, `/ (root)` folder
5. Click **Save**
6. Site will be live at `https://yourusername.github.io/reponame/`

## Edit Content

Open `data/profile.json` and modify the JSON. No HTML/CSS knowledge needed for content updates.

## No Build Step

Pure static HTML/CSS/JS. Open `index.html` directly in your browser to preview.
