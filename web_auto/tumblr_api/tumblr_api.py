from selenium import webdriver


d = webdriver.PhantomJS()
#http://21-pantaloons.tumblr.com/api/read?start=0&num=20
d.get("http://21-pantaloons.tumblr.com/api/read?start=0&num=20")

