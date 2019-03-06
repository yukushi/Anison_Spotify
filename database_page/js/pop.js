window.onload=autoPOP;

function autoPOP()
{
	var x = document.getElementsByTagName('a');
	for (var i=0;i<x.length;i++)
	{
		if (x[i].getAttribute('className') == 'popup' || x[i].getAttribute('class') == 'popup')
		{
			x[i].onclick = function () {
			return winOpen(this.href)
			}
			x[i].title += '(Popup)';
		}
	}
};

function winOpen(url) {
	window.open(
		url,
		'popup',
		'width=360,height=240'
	);

	return false;
};