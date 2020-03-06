from django.shortcuts import render

def mainPage(request):
	return render(request, "index.html")

def testCallback(request):
	return render(request, "testCallback.html")