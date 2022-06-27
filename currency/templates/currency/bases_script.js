document.title = 'Srrafa.com'
const style = document.createElement('style')
const bootstrap = document.createElement('link')
const fontawsome = document.createElement('link')
bootstrap.rel = "stylesheet"
bootstrap.href = "https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css"
bootstrap.integrity = "sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC"
bootstrap.crossOrigin = "anonymous"
fontawsome.href = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css"
fontawsome.rel = "stylesheet"
fontawsome.crossOrigin = "anonymous"
fontawsome.referrerPolicy = "no-referrer"
fontawsome.integrity = "sha512-KfkfwYDsLkIlwQp6LFnl8zNdLGxu9YAA1QvwINks4PhcElQSvqcyVLLD9aMhXd13uQjoXtEKNosOWaZqXgel0g=="

style.textContent = `
@import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap');

*{
    font-family: 'Roboto', sans-serif;
    box-sizing: border-box;
    scroll-behavior: smooth;

}
::-webkit-scrollbar {
    width: 4px;
    height:4px
  }
::-webkit-scrollbar-track {
    background: #f1f1f1;
  }
::-webkit-scrollbar-thumb {
    background: #0d6efd;
  }
::-webkit-scrollbar-thumb:hover {
    background: #555;
  }
.chip-con{
    display: flex;
    justify-content: flex-start;
    align-items: center;
    flex-wrap: wrap;
}
.chip{
    margin:  0.5rem;
    cursor: pointer;
    width: fit-content;
    padding-right: 1rem;
    background-color: #cbcbcb33;
    font-size: 0.8em;
    font-weight: bolder;
    display: flex;
    align-items: center;
    transition:all linear 0.2s;
}
.chip:hover{
    background-color: #4a494933;
    transform:scale(1.1);
    color:#0d6efd;
}
.chip-con .active{
    background-color: #4a494933;
    transform:scale(1.1);
    color:#0d6efd;
}
.table>:not(caption)>*>*{
    font-size: 14px;
    font-weight:500;
    padding:1rem 0.5rem !important;
}
`
document.head.appendChild(style)
document.head.appendChild(bootstrap)
document.head.appendChild(fontawsome)
const mathfilters = document.createTextNode(`{% load mathfilters %}`)
console.log(mathfilters)
document.body.insertBefore(mathfilters ,document.body.firstElementChild)

const chips = document.createElement('div')
chips.innerHTML = `    <div class='chip-con'>
{% for baseKey in bases %}
<div id="{{ baseKey }}" onclick="changeView('{{baseKey}}')" class="rounded-pill chip {% if baseKey == 'USD' %} active {% endif %}" >
    <img class="rounded-circle" style="background-color: #fff; width: 25px; height: 25px; margin-right: 0.5rem;" src="https://countryflagsapi.com/svg/{{baseKey|slice:2|lower}}" > {{baseKey}}
</div>
{% endfor %}
</div>`

const table = document.createElement('table')
table.className = 'table table-hover'

table.innerHTML = ` <thead>
<tr>
    <td>Name</td>
    <td>Bye</td>
    <td>Sell</td>
    <td>24h</td>
</tr>
</thead>
<tbody id="view">
{% for com in data %}

<tr>
    <td> <img class="rounded-circle" style="width: 30px; height: 30px; margin-right: 0.5rem;" src="https://countryflagsapi.com/svg/{{com.normal_currency.sympol|slice:2|lower}}" /> {{ com.normal_currency.name }}</td>
    <td>{{com.bye_value|floatformat:2}} {{com.normal_currency.sympol}}</td>
    <td>{{ com.sell_value|floatformat:2 }} {{com.normal_currency.sympol}}</td>
    <td style="color:{% if com.h24 > 0 %}green{% else %}red{% endif %};">{% if com.h24 > 0 %} <i style="color:green; margin-right:0.25" class="fa-solid fa-arrow-up"></i> {% else %} <i style="color:red; margin-right:0.25" class="fa-solid fa-arrow-down"></i> {% endif %} {{com.h24}} %</td>
</tr>

{% endfor %}
</tbody>`
const container = document.createElement('div')
container.id = 'container'
container.style.maxWidth = '600px'
container.style.maxHeight='100%'
container.style.overflowY='scroll'
container.style.margin = '1rem auto'
container.style.padding='0 1rem'
container.style.border = '1px solid #fff'
container.style.borderRadius = '10px'
const visitUs = document.createElement('h5')
visitUs.innerHTML =`Visit us <a href='http://localhost:8000' target='_'>Srrafa.com</a>`
visitUs.style.textAlign = 'center'
container.appendChild(visitUs)
container.appendChild(chips)
container.appendChild(table)
// container.appendChild(visitUs)
document.currentScript.parentElement.appendChild(container)


const fetchData = async (sympol) =>{
    const res = await fetch('http://localhost:8000/frame-data/', {
        method:'POST',
        headers:{
            'Content-type':'application/json'
        },
        body:JSON.stringify({sympol})
    })
    const data = await res.json()
    return data
}

const changeView = async (sympol) => {
    const chips =  document.querySelectorAll('.chip')
    for (let index = 0; index < chips.length; index++) {
        if (chips[index].classList.contains('active'))
            chips[index].classList.remove('active')
        if (chips[index].id == sympol)
        chips[index].classList.add('active')
    }
    const data = await fetchData(sympol)
    const htmlArr = data.map(com => {
        return(
        `<tr>
            <td> <img class="rounded-circle" style="width: 30px; height: 30px; margin-right: 0.5rem;" src="https://countryflagsapi.com/svg/${com.normal_currency.sympol.substring(0,2).toLowerCase()}" /> ${ com.normal_currency.name }</td>
            <td>${Math.round((com.bye_value +Number.EPSILON)*100)/100} ${com.normal_currency.sympol}</td>
            <td>${ Math.round((com.sell_value+Number.EPSILON)*100)/100 } ${com.normal_currency.sympol}</td>
            <td style="color:${com.h24>0?'green':'red'}">${com.h24 > 0? '<i style="color:green; margin-right:0.25rem" class="fa-solid fa-arrow-up"></i>':'<i style="color:red; margin-right:0.25rem" class="fa-solid fa-arrow-down"></i>'} ${com.h24} %</td>
        </tr>`
        )
    })

    document.getElementById('view').innerHTML = htmlArr.join(' ')
}
