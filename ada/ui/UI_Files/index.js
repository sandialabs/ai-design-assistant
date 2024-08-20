import { updateGraphicWindow } from './geometryWindowHandler.js'
window.runMain  = runMain;
window.copyText = copyText;


async function onLoad() {
    const windowHeight = window.innerHeight;
    const mainColumns = document.querySelectorAll('.main-column');
    mainColumns.forEach(col => {
    col.setAttribute('style','height:'+String(windowHeight-58)+'px')
    });

    const output_div = document.getElementById("main-body-scroll-wrapper");
    const f_navbar_div = document.getElementById("file-sidebar-body");
    const g_navbar_div = document.getElementById("geometry-sidebar-body");
    const a_navbar_div = document.getElementById("analysis-sidebar-body");
    const d_navbar_div = document.getElementById("data-sidebar-body");

    var response;

    var post_data = JSON.stringify( {queryText: "", callMode: "Functions"}) ;
    response = await fetch("", {
      method: "POST",
      body: post_data,
      headers: {
        "Content-type": "application/json; charset=UTF-8",
        'Content-Length': new TextEncoder().encode(post_data).length
      }
    })
    .catch(error => console.error(error));
    const jsonData = await response.json();

    output_div.innerHTML = jsonData.mainBodyText ; 
    f_navbar_div.innerHTML = jsonData.filetreeText ;
    g_navbar_div.innerHTML = jsonData.geometryText ;
    a_navbar_div.innerHTML = jsonData.analysisText ;
    d_navbar_div.innerHTML = jsonData.dataText ;

    const tableRows = document.querySelectorAll('.file-row');
    tableRows.forEach(row => {
    row.addEventListener('click', onRowClick);
    });

    const send_buttons = document.querySelectorAll('.send-button');
    send_buttons.forEach(sb => {
    sb.addEventListener('click', runMain);
    });

    const copy_buttons = document.querySelectorAll('.copy-button');
    copy_buttons.forEach(cb => {
    cb.addEventListener('click', copyText);
    });

}

async function runMain(event) {

    let response = await executeCall();
    setTimeout(scrollToBottomBody, 20);

}

async function copyText(event) {
    // Access the clicked row and its content
    const clickedButton = event.currentTarget;
    const parentDiv = clickedButton.parentNode;
    const copy_string = parentDiv.innerHTML.split("</button>").pop();
    // console.log(copy_string );
    navigator.clipboard.writeText(copy_string);
    clickedButton.children[0].style.opacity=0;
    setTimeout(function (){
    clickedButton.children[0].style.opacity=1;
    }, 100);
}

async function executeCall() {
    const input_text = document.getElementById("input_text").value;
    document.getElementById("input_text").value = "" ;
    const output_div = document.getElementById("main-body-scroll-wrapper");
    const f_navbar_div = document.getElementById("file-sidebar-body");
    const g_navbar_div = document.getElementById("geometry-sidebar-body");
    const a_navbar_div = document.getElementById("analysis-sidebar-body");
    const d_navbar_div = document.getElementById("data-sidebar-body");

    const input_callMode = document.getElementById('mode-selector-dropdown').value;

    var response;

    if (input_text != '') {
        // Add something that gives a status...
        var pstr = ''
        pstr += '<div class="body-cell">\n'
        pstr += '    <div class="io-cell input-cell">\n'
        pstr += '        <div class="label io-text">Query [*]</div>\n'

        pstr += '        <div class="query-cell io-text">'
        pstr += input_text
        pstr += '</div>\n'

        pstr += '    </div>\n'
        pstr += '    <div class="io-cell output-cell">\n'
        pstr += '        <div class="label io-text">Interpretation [*]</div>\n'
        
        pstr += '        <div class="interpretation-cell io-text">'
        pstr += input_callMode
        pstr += '</div>\n'
        
        pstr += '    </div>\n'
        pstr += '    <div class="io-cell output-cell">\n'
        pstr += '        <div class="label io-text">Response [*]</div>\n'
        pstr += '        <div class="response-cell io-text">Working...</div>\n'
        pstr += '    </div>\n'
        pstr += '</div>\n'
        // console.log(pstr)
        output_div.innerHTML += pstr; 
        // updateGraphicWindow(jsonData.graphicWindow);
        setTimeout(scrollToBottomBody, 20);

        var post_data = JSON.stringify( {queryText: input_text, callMode: input_callMode}) ;
        response = await fetch("", {
          method: "POST",
          body: post_data,
          headers: {
            "Content-type": "application/json; charset=UTF-8",
            'Content-Length': new TextEncoder().encode(post_data).length
          }
        })
        .catch(error => console.error(error));
        const jsonData = await response.json();

        output_div.innerHTML = jsonData.mainBodyText ; 
        f_navbar_div.innerHTML = jsonData.filetreeText ;
        g_navbar_div.innerHTML = jsonData.geometryText ;
        a_navbar_div.innerHTML = jsonData.analysisText ;
        d_navbar_div.innerHTML = jsonData.dataText ;

        updateGraphicWindow(jsonData.graphicWindow);

    const tableRows = document.querySelectorAll('.file-row');
    tableRows.forEach(row => {
    row.addEventListener('click', onRowClick);
    });

    }
    return Promise.resolve(response);
}

function scrollToBottomBody() {
    var getLastElemIndex = document.getElementsByClassName("body-cell").length -1;
    var nextDiv ; 
    if (getLastElemIndex != -1) {
        nextDiv = document.getElementsByClassName("body-cell")[getLastElemIndex];
        // console.log(nextDiv.innerHTML)
        document.getElementsByClassName("body-cell")[getLastElemIndex].scrollIntoView({ behavior: "smooth", block: "start" });
    } 
}

function getSelectorBackgroundColor(value) {
    if (value === 'Functions') {
      return '#0065cc';
    } else if (value === 'RAG') {
      return '#009e73';
    } else if (value === 'RAG-C') {
      return '#56b4ff';
    } else if (value === 'LLM') {
      return '#e69f00';
    } else {
      // Default background color
      return '#d55e00';
    }
}

function nextMode() {
    var selectElement = document.getElementById('mode-selector-dropdown');
    var value = selectElement.value;
    if (value === 'Functions') {
      selectElement.value = 'RAG';
      selectElement.style.backgroundColor = getSelectorBackgroundColor('RAG');
    } else if (value === 'RAG') {
      selectElement.value = "RAG-C";
      selectElement.style.backgroundColor = getSelectorBackgroundColor('RAG-C');
    } else if (value === 'RAG-C') {
      selectElement.value = "LLM";
      selectElement.style.backgroundColor = getSelectorBackgroundColor('LLM');
    } else if (value === 'LLM') {
      selectElement.value = "Functions";
      selectElement.style.backgroundColor = getSelectorBackgroundColor('Functions');
    } else {
      // Do nothing;
    }
}


document.addEventListener('DOMContentLoaded', function () {
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
        // if (event.shiftKey && event.key === 'Enter') {
          runMain();
        }
      });


  var selectElement = document.getElementById('mode-selector-dropdown');
  selectElement.addEventListener('change', function () {
    var selectedValue = selectElement.value;
    selectElement.style.backgroundColor = getSelectorBackgroundColor(selectedValue);
  });


  var inputText = document.getElementById('input_text');
  document.addEventListener('keydown', function (event) {
    // Check if the pressed key is the Tab key (key code 9)
    if (event.key === 'Tab' && document.activeElement === inputText) {
      event.preventDefault();
      // Call the changeBackgroundColor function
      nextMode();
    }

  });

  window.onload = onLoad();

});



async function onRowClick(event) {
    // Access the clicked row and its content
    const clickedRow = event.currentTarget;
    const rowData = Array.from(clickedRow.children).map(cell => cell.textContent);

    // console.log('hicody')
    // Print the contents to console.log
    // console.log('Clicked Row:', rowData);

    const output_div = document.getElementById("main-body-scroll-wrapper");
    const f_navbar_div = document.getElementById("file-sidebar-body");
    const g_navbar_div = document.getElementById("geometry-sidebar-body");
    const a_navbar_div = document.getElementById("analysis-sidebar-body");
    const d_navbar_div = document.getElementById("data-sidebar-body");

    var response;

    var post_data = JSON.stringify( {queryText: rowData[0]+rowData[1], callMode: "_FileClick"}) ;
    response = await fetch("", {
      method: "POST",
      body: post_data,
      headers: {
        "Content-type": "application/json; charset=UTF-8",
        'Content-Length': new TextEncoder().encode(post_data).length
      }
    })
    .catch(error => console.error(error));
    const jsonData = await response.json();

    output_div.innerHTML = jsonData.mainBodyText ; 
    f_navbar_div.innerHTML = jsonData.filetreeText ;
    g_navbar_div.innerHTML = jsonData.geometryText ;
    a_navbar_div.innerHTML = jsonData.analysisText ;
    d_navbar_div.innerHTML = jsonData.dataText ;

    const tableRows = document.querySelectorAll('.file-row');
    tableRows.forEach(row => {
    row.addEventListener('click', onRowClick);
    });

};











// okabe_ito_custom_cycle :  ['#0065cc', '#e69f00', '#009e73', '#d55e00', '#56b4ff', '#fca7c7', '#ede13f', '#666666', '#000000']
//                                blue,    orange,    green,     red,      l blue,     pink,      yellow,     grey,      black