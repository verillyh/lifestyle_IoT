# Lifestyle IoT Solution 
This repo houses the code for an IoT solution containing:
- Smart lock
- Smart light
- Smart speaker

For setting up, make sure you run the following commands

Go to your Raspberry Pi for the smart speaker, and install the following bluetooth package
```
sudo apt install bluetooth bluez-utils blueman
```

```
pip install -r requirements.txt
cd website
npm install
```

To run the website, make sure to do the following commands on DIFFERENT terminals

```
cd website 
npm run dev
```

```
cd website
python app.py
```

```
cd edge
python lock_edge.py
```