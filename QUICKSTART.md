# QUICK START GUIDE

## Installation (One-time setup)

### Option 1: Automatic Setup (macOS/Linux)
```bash
cd reelgood-scraper
./setup.sh
```

### Option 2: Manual Setup (All platforms)
```bash
cd reelgood-scraper
pip3 install -r requirements.txt
```

If you get permission errors, try:
```bash
pip3 install -r requirements.txt --user
```

---

## Usage Examples

### Single URL
```bash
python3 reelgood_scraper.py https://reelgood.com/movie/inception-2010
```

### Multiple URLs (command line)
```bash
python3 batch_scraper.py \
  https://reelgood.com/movie/inception-2010 \
  https://reelgood.com/show/breaking-bad-2008
```

### Multiple URLs (from file)
Edit `urls.txt` to add your URLs, then run:
```bash
python3 batch_scraper.py --file urls.txt
```

### Debug Mode
```bash
python3 reelgood_scraper.py https://reelgood.com/movie/the-matrix-1999 --debug
```

---

## Project Structure

```
reelgood-scraper/
├── reelgood_scraper.py  # Main scraper script
├── batch_scraper.py     # Batch processing script
├── requirements.txt     # Python dependencies
├── setup.sh            # Auto-setup script (macOS/Linux)
├── urls.txt            # Sample URLs file
├── README.md           # Full documentation
└── QUICKSTART.md       # This file
```

---

## Troubleshooting

**"No module named 'requests'"**
→ Run: `pip3 install requests beautifulsoup4`

**"No platforms detected"**
→ Try with `--debug` flag to see what's being extracted

**Permission denied when running setup.sh**
→ Run: `chmod +x setup.sh` then try again

---

## Next Steps

- Read the full README.md for detailed documentation
- Edit urls.txt to add your favorite shows/movies
- Run batch_scraper.py to check multiple titles at once

Happy scraping! 🎬
