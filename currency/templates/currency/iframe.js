// <!-- <p style="display: inline;">this is my iframe</p> -->    
var span = document.createElement('span')
span.textContent= ' this is my iframe '
document.currentScript.parentElement.appendChild(span)