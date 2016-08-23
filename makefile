#Default arg to build:
ifndef ${draw}
	draw := "circles"
endif


all :
	python ./main.py ${draw}

clean :
	rm imgs/*.png

