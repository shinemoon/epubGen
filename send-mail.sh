#!/bin/bash
SUBJECT="[epubGen]电子书生成完毕"
MAILFROM="noreply@`hostname -f`"
MAILTO="shinemoon@foxmail.com"
#ATTACHMENT="working/dcb74152c0/凡人修仙传.epub"
ATTACHMENT="tags"
MAILPART=`uuidgen` ## Generates Unique ID as boundary
MAILPART_BODY=`uuidgen` ## Generates Unique ID as boundary

(
 echo "From: $MAILFROM"
 echo "To: $MAILTO"
 echo "Subject: $SUBJECT"
 echo "MIME-Version: 1.0"
 echo "Content-Type: multipart/mixed; boundary=\"$MAILPART\""
 echo ""
 echo "--$MAILPART"
 echo "Content-Type: multipart/alternative; boundary=\"$MAILPART_BODY\""
 echo ""
 echo "--$MAILPART_BODY"
 echo "Content-Type: text/plain; charset=UTF-8"
 echo "This is TEXT part and below is HTML part"
 echo "--$MAILPART_BODY"
 echo "Content-Type: text/html; charset=UTF-8"
 echo ""
 echo "<html><body><div>THIS IS HTML PART</div></body></html>"
 echo "--$MAILPART_BODY--"

 echo "--$MAILPART"
 echo 'Content-Type: text/plain; name="'$(basename $ATTACHMENT)'"'
 echo "Content-Transfer-Encoding: base64"
 echo ""
 openssl base64 < $ATTACHMENT;
 echo "--$MAILPART--"
)  | sendmail -t

