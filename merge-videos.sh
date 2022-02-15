for f in slides/*.mp4;
do
	num="${f:7:2}"
	ffmpeg \
		-i videos/"$num"-video.mp4 \
		-i slides/"$num"-slides.mp4 \
		-filter_complex '[0:v]scale=w=1024:h=572,pad=1024:ih+572:x=0:y=571[int];[int][1:v]overlay=0:0[vid]' \
		-map "[vid]" \
		-map 0:a \
		-map 0:s? \
		-c:s copy \
		-c:v libx264 \
		-crf 23 \
		-preset veryfast \
		"$num"-final.mp4
done
