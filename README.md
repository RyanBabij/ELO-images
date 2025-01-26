# ELO images
Python script to calculate ELO scores between a collection of images. Why use tier lists when you can get the real data.

It will take all the images from a directory and show 2 of them side-by-side. Press left arrow if you prefer the left image, right arrow if you prefer the right image. Image rendering is a bit laggy I'm afraid. Click the X or press ESC when you are done and the ELOs will be updated. You should be able to add and remove images and it will keep updating the rankings without problems.

Written with GPT.

Default base rating is set at 1000, but I prefer to lower it to 50 for readability.

The algorithm picks the image which has not been picked for the longest, and compares it with a random image. This seems to get decent results without making things too complicated.

It takes about 3n trials to get a reasonably accurate ranking. This is a bit frustrating as I feel like a better algorithm would do okay with 2n trials.


```
py path\to\elo_image.py "path\to\images" --base_rating 50 --window_width 1400 --window_height 900
```

##Sample output

The program:

![Screenshot of program](https://raw.githubusercontent.com/RyanBabij/ELO-images/refs/heads/main/SampleOutput/sample.png)

JSON output:

```
{
    "elo_ratings": {
        "Tick Tock Clock.png": 139,
        "Bobomb Battlefield.png": 121,
        "Cool Cool Mountain.png": 110,
        "Hazy Maze Cave.png": 104,
        "Whomps Fortress.png": 95,
        "Lethal Lava Land.png": 78,
        "Shifting Sand Land.png": 72,
        "Wet Dry World.png": 39,
        "Big Boos Haunt.png": 32,
        "Rainbow Ride.png": 23,
        "Jolly Roger Bay.png": 21,
        "Snowmans Land.png": 0,
        "Tall Tall Mountain.png": -13,
        "Tiny Huge Island.png": -17,
        "Dire Dire Docks.png": -54
    },
```


## Dependencies:

Developed with Python 3.13.1.

```
py -m pip install pillow
py -m pip install tkinter
```
