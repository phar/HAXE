# HAXE - a pyqt based hex editor

python hex editor forked fromfrom csarn as qthexedit.

currently supporting such wild features as:
	pure python3/pyqt5 (works on my mac!)
	copy!
	paste!
	cut!
	insert!
	delete!
	largefile support(a compromis that removes the above features.. labeled as a feature!)	
	the above features from ascii or binary sides depending on where you placed the cursur!
	active/passive cursor so you can tell where you are!
	arrow key based cursor movement and selection using shift!
	almost has an undo stack!
	almost has a dynamic plugin architecture!
	almost has functional structure support!
	interactive python with a straightforward-ish Help() command and API
	bugs i havnt found in my obsessive feature adding!
	dynamic high contrast highlighting scheme 
	
still to come:
	syncronizing documents 
	different then ascii encodings
	graphical view (bytes mapped to colors)
	"make structure at location" and assosciated gui elements
	plguin api that supports infinite expansion *cough*

<img src="imgs/snap.png">

<pre>
$ pythonw haxe.py  -f example/testfile
</pre>
