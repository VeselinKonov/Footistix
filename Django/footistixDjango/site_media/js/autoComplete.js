const searchWrapper = document.querySelector(".search-input");
const inputBox = searchWrapper.querySelector("input");
const suggBox = searchWrapper.querySelector(".autocom-box");

inputBox.oninput = (e)=>{
  // console.log(suggestionsArr)
  let userData = e.target.value; //user entered data
  let suggestionsNamesOnly = [];
  let suggestions = [];
  suggestionsArr.forEach(element => suggestionsNamesOnly.push(element['name']))
  if(userData){
    suggestions = suggestionsNamesOnly.filter((data)=>{
      return data.toLocaleLowerCase().startsWith(userData.toLocaleLowerCase());
      
    });
    suggestions = suggestions.map((data)=>{
      return data = '<li onclick="goTo(this);">' + data + '</li>'
    })
    
  }else{
    searchWrapper.classList.remove("active");
  }
  showSuggestions(suggestions)
}

function showSuggestions(list){
  let listData;
  if(list.length){
    listData = list.join('');
    searchWrapper.classList.add("active");
    suggBox.innerHTML = listData
  }
}

function goTo(li){
  const searchedObject = suggestionsArr.find(element => element['name'] == li.innerHTML);
  url = searchedObject['hyperlink']
  // url = suggestionsArr(li.innerHTML)
  window.location.replace(url);
}

function convertToSlug(Text) {
  return Text.toLowerCase()
             .replace(/ /g, '-')
             .replace(/[^\w-]+/g, '');
}