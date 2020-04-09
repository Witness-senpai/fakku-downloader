# fakku-downloader

Fakku-downloadred - this is python script thats allows download manga dyrectly from fakku.net.

### The problem

*Fakku.net manga reader has a good protect from download.*

As far as I know, Manga reader first decodes the encrypted image and then displays it on the html canvas. This is done so tricky that I could not find a way to automate the downloading of canvas because the JS functions for this are blocked in the domain. Therefore, in order to download manga, you need to do some non-trivial actions manually. And this will have to be done separately for each page.

### The easyes solution

In my opinion, the simplest and fastest solution for downloading manga from fakku.net is to simply open it in a browser and save a screenshot of each page. Fakku-downloader automates this process in background using headless browser.

## How to launch

* Download [ChromeDriver](https://chromedriver.chromium.org/downloads) the same version as you Chrome Browser and move it in root folder.
(Rename it to **chromedriver.exe**)
* Create **urls.txt** file in root folder and write into that urls of manga one by line
* Write the command <code>python main.py</code>

## Some features 
* Use key -t for set timeout between loading the pages. If quality of .png is bad, or program somewhere crush its can help.
* Use keys -l and -p for write the login and password in command
* More technical information you can find in comments to code

---

## Work example

1. After downloading the repository, chromedriver and creating urls.txt file, root folder will be like this:
<p align="center">
	<img src="https://github.com/Witness-senpai/fakku-downloader/blob/master/readme_png/1.PNG" width="800">
</p>
2. Urls in urls.txt views like this:
<p align="center">
	<img src="https://github.com/Witness-senpai/fakku-downloader/blob/master/readme_png/2.PNG" width="800">
</p>
3. Write the command: python main.py
<p align="center">
	<img src="https://github.com/Witness-senpai/fakku-downloader/blob/master/readme_png/3.PNG" width="800">
</p>
4. If you launch program in first time, you need to login in opening browser and press enter in console. After that program save the cookies and will be use it in next runs in headless browser mode and skeep this step.
<p align="center">
	<img src="https://github.com/Witness-senpai/fakku-downloader/blob/master/readme_png/4.PNG" width="800">
</p>
5. Downloading process in progress
<p align="center">
	<img src="https://github.com/Witness-senpai/fakku-downloader/blob/master/readme_png/5.PNG" width="800">
</p>
6. The program will create its own folder for each manga in urls.txt
<p align="center">
	<img src="https://github.com/Witness-senpai/fakku-downloader/blob/master/readme_png/6.PNG" width="800">
</p>
7. And inside in each folder you can see the manga pages in the most affordable quality as in a browser.
<p align="center">
	<img src="https://github.com/Witness-senpai/fakku-downloader/blob/master/readme_png/7.PNG" width="800">
</p>
