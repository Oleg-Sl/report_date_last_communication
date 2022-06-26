export default class TableStatistic {
    constructor(table, user, loader) {
        this.table = table;
        // контейнер заголовка таблицы
        this.tableHeader = this.table.querySelector("thead");
        this.tableBody = this.table.querySelector("tbody");
        
        this.user = user;
        this.loader = loader;
        
    }

    async init() {
        // обработчик перетаскивания таблицы по нажатию кнопки мыши
        this.handlerDragnDrop();
        // обработчик изменения ширины столбцов таблицы мышью
        this.handlerResizeWidthColumn();
        // инициализация обработчиков событий таблицы: вертикальны скролл страницы, горизантальный скролл таблицы
        this.initHandlerScroll();
        // // обработчик событий наведения на пользователя или компанию
        // this.eventHoverElementsTable();

    }

    showTable() {
        this.table.classList.remove("d-none");
        this.loader.classList.add("d-none");
    }

    hideTable() {
        this.table.classList.add("d-none");
        this.loader.classList.remove("d-none");
    }

    // инициализация событий таблицы: вертикальны скролл страницы, горизантальный скролл таблицы
    initHandlerScroll() {
        // обработчик вертикального скролла страницы - залипание первой строки таблицы
        document.addEventListener("scroll", (e) => requestAnimationFrame(() => {
            let elem = document.getElementsByTagName("table")[0];
            let offsetTop = $(document).scrollTop();
            if (elem.offsetTop < offsetTop) {
                $('th').css({
                    "top": offsetTop - elem.offsetTop
                })
            }
            else {
                $('th').css({"top": 0})
            }
        }))

        // обработчик горизантального скролла таблицы - залипание первого столбца таблицы
        this.table.addEventListener('scroll', (event)=>{
            let offsetLeft = this.table.scrollLeft;
            // console.log("offsetLeft => ", offsetLeft);
            $('.col-company').css({
                "left": offsetLeft
            })
        });
    }
    
    // обработчик перетаскивания таблицы по нажатию кнопки мыши
    handlerDragnDrop() {
        $("table").on("mousedown", function(event) {
            if (event.target.tagName == "SPAN" || event.target.tagName == "A" || event.which !== 1) {
                return;
            }
            let elem = document.getElementsByTagName("table")[0];
            let elemCursor = document.getElementsByTagName("body")[0];
            elem.onselectstart = () => false;
            elemCursor.style.cursor = "grab";
            // стартовая позиция курсора на экране
            let cursorStart = {
                "X": event.pageX, 
                "Y": event.pageY
            }
            // координаты таблицы на странице
            let scrollStart = {
                "X": elem.scrollLeft,
                "Y": elem.scrollTop
            }
            // максимальное значение ScrolLeft
            let maxScrollWidth = elem.scrollWidth - elem.offsetWidth;
            // функция перемещения таблицы по горизонтали
            function onMouseMove(event) {
                
                if (event.which !== 1) {
                    disabledDragDrop();
                }
                let offset = scrollStart.X - event.pageX + cursorStart.X;
                if (offset < 0) {
                    offset = 0;
                }
                if (offset > maxScrollWidth) {
                    offset = maxScrollWidth;
                }
                elem.scrollLeft = offset;
            }
            // установка обработчика перемещения мыши
            document.addEventListener('mousemove', onMouseMove);
    
            // событие при отпускании кнопки мыши
            $(document).on("mouseup",  function() {
                disabledDragDrop();
            });

            function disabledDragDrop() {
                // console.log("disabledDragDrop");
                document.removeEventListener('mousemove', onMouseMove);
                $("table").onmouseup = null;
                elemCursor.style.cursor = "default";
            };
    
        })
    }

    // обработчик изменения ширины столбцов таблицы - необходимо инициализировать после перерисовки таблицы
    handlerResizeWidthColumn() {
        // соответствие типу колонки ее ширины в "px" и "fr"
        const columnTypeToRatioMap = {
            'numeric-short': {  // столбцы - ИНН
                'min': 60,
                'max': 1
            },
            'numeric-medium': { 
                'min': 75,
                'max': 1.2
            },
            'numeric-long': { // столбцы - общ. сумма успешн. и в работе по компании 
                'min': 92,
                'max': 1.5
            },
            'text-short': { // столбцы - ДПК
                'min': 75,
                'max': 1
            },
            'text-long': {  // столбцы - компания, менеджер
                'min': 110,
                'max': 2.5
            }
        };
        
        const columns = [];
        let headerBeingResized;

        const onMouseMove = (e) => requestAnimationFrame(() => {
            if (e.which !== 1) {
                disabledResizeWidthColumn();
            }
            // console.log(">>> ", headerBeingResized);
            const horizontalScrollOffset = this.table.scrollLeft;
            // console.log("Смещение таблицы по оси X = ", horizontalScrollOffset);
            // console.log("Позиция курсора = ", e.clientX);
            // console.log("Текущее положение столбца = ", headerBeingResized.offsetLeft);
            const width = (horizontalScrollOffset + e.clientX) - headerBeingResized.offsetLeft;
            const column = columns.find(({ header }) => header === headerBeingResized);
            const min = column.minWidth

            // установить ширину столбца меньше минимального значения невозможно
            column.size = Math.max(min, width) + 'px';
            
            columns.forEach((column) => {
                if(column.size.startsWith('minmax')){
                    // console.log("column = ", column);
                    column.size = parseInt(column.header.clientWidth, 10) + 'px';
                    // console.log("column after = ", column);
                }
            });
            
            
            let sortPositionColumn = columns.map(({position}) => position).sort(compareNumeric);
            let sizeColumn = {};
            for (let col of columns) {
                sizeColumn[col.position] = col.size;
            }
            let arrSizeColumn = sortPositionColumn.map((ind) => sizeColumn[ind]);
            // console.log("arrSizeColumn = ", arrSizeColumn);
            this.table.style.gridTemplateColumns = arrSizeColumn.join(' ');
            localStorage.setItem('grid-template-columns', arrSizeColumn.join(' '));
        });

        const onMouseUp = () => {
            disabledResizeWidthColumn();
        };

        const disabledResizeWidthColumn = () => {
            window.removeEventListener('mousemove', onMouseMove);
            window.removeEventListener('mouseup', onMouseUp);
            headerBeingResized.classList.remove('header--being-resized');
            headerBeingResized = null;
        }

        const initResize = (event) => {
            // родительский блок ячейки таблицы в которой находится элемент "span" по которому произошло событие
            headerBeingResized = event.target.parentNode;
            window.addEventListener('mousemove', onMouseMove);
            window.addEventListener('mouseup', onMouseUp);
            headerBeingResized.classList.add('header--being-resized');
        };

        document.querySelectorAll('th').forEach((header) => {
            if (header.dataset.type && header.dataset.position) {
                const position = header.dataset.position;
                const min = columnTypeToRatioMap[header.dataset.type]['min'];
                const max = columnTypeToRatioMap[header.dataset.type]['max'];
                columns.push({
                    position,
                    minWidth: min,
                    header, 
                    size: `minmax(${min}px, ${max}fr)`,
                });
                header.querySelector('.resize-handle').addEventListener('mousedown', initResize);
            }
        });
    }

    renderTable(companySummary, directionSummary, companySummaryByDirection) {
        this.companySummary = companySummary; 
        this.directionSummary = directionSummary;
        this.companySummaryByDirection = companySummaryByDirection;

        let contentHeadHTML = this.renderTableHead();
        this.tableHeader.innerHTML = contentHeadHTML;

        this.table.style.gridTemplateColumns = arrSizeColumn.join(' ');
        this.showTable();
        // this.handlerResizeWidthColumn();
    }

    // создание заголовка таблицы
    renderTableHeaderToHTML(data) {
        let directions = this.directionSummary;

        let startColumnWithDirData = 6;     // столбец с которого начинаются данные по направлениям
        let numberColumnsInDir = 2;         // столбцов данных в одном направлении
        // масссив с шириной колонок
        this.arrSizeColumn = ["minmax(150px, 2.5fr)", "minmax(120px, 1.5fr)", "minmax(100px, 1.5fr)", "minmax(95px, 1.2fr)", "minmax(95px, 1.2fr)"];
        
        let firstRowHTML = "";
        let secondRowHTML = "";
        let thirdRowHTML = `
            <th class="col-company header-count-active-deal" style="grid-column: $1/2;"></th>
            <th scope="col" colspan="${startColumnWithDirData}" class="header-count-active-deal" style="grid-column: 2/${startColumnWithDirData};">
                <div>Активные сделки</div>
            </th>
        `;

        for(let dirId of directions) {
            let dirName = directions[dirId].name;
            let numberActiveDealInDir = directions[dirId].count_active_deal;
            firstRowHTML += `
                <th scope="col" colspan="${numberColumnsInDir}" class="header-th-direction" style="grid-column: ${startColumnWithDirData}/${startColumnWithDirData + numberColumnsInDir}; grid-row: 1/2">
                    <div>${dirName}</div>
                    <span class="resize-handle"></span>
                </th>
            `;
            secondRowHTML += `
                <th scope="col" class="header-th-direction-data" data-type="numeric-medium" data-position="${startColumnWithDirData + 1}">Сумма в работе <span class="resize-handle"></span></th>
                <th scope="col" class="header-th-direction-data" data-type="numeric-medium" data-position="${startColumnWithDirData + 2}">Сумма успешных <span class="resize-handle"></span></th>
            `;
            thirdRowHTML += `
                <th scope="col" colspan="${numberColumnsInDir}" class="header-count-active-deal directory-column-border-left-border-left" style="grid-column: ${startColumnWithDirData}/${startColumnWithDirData + numberColumnsInDir};">
                    <div>${numberActiveDealInDir}</div>
                </th>
            `;

            startColumnWithDirData += numberColumnsInDir;

            this.arrSizeColumn.push("minmax(90px, 1.2fr)");
            this.arrSizeColumn.push("minmax(90px, 1.2fr)");
        }

        let contentHTML =`
            <tr class="text-center">
                <th scope="col" rowspan="2" class="col-company header-th-data header-th-sort-data" data-type="text-long" data-position="1">
                    Компания
                    <span class="resize-handle"></span>
                    <span class="sort-company-top">
                        <i data-order="name" class="bi bi-caret-up-fill sort-button" id="sorting-company-asc"></i>
                    </span>
                    <span class="sort-company-bottom">
                        <i data-order="-name" class="bi bi-caret-down-fill sort-button" id="sorting-company-desc"></i>
                    </span>
                </th>
                <!-- <th scope="col" rowspan="2" class="header-th-data header-th-sort-data" data-type="numeric-short" data-position="2">
                    ИНН 
                    <span class="resize-handle"></span>
                    <span class="sort-inn-top">
                        <i data-order="inn" class="bi bi-caret-up-fill sort-button" id="sorting-inn-asc"></i>
                    </span>
                    <span class="sort-inn-bottom">
                        <i data-order="-inn" class="bi bi-caret-down-fill sort-button" id="sorting-inn-asc"></i>
                    </span>    
                </th> -->
                <th scope="col" rowspan="2" class="header-th-data header-th-sort-data" data-type="text-long"  data-position="3">
                    Менеджер 
                    <span class="resize-handle"></span>
                    <span class="sort-responsible-top">
                        <i data-order="lastname" class="bi bi-caret-up-fill sort-button" id="sorting-responsible-asc"></i>
                    </span>
                    <span class="sort-responsible-bottom">
                        <i data-order="-lastname" class="bi bi-caret-down-fill sort-button" id="sorting-responsible-asc"></i>
                    </span>
                </th>
                
                <th scope="col" rowspan="2" class="header-th-data header-th-sort-data" data-type="text-short"  data-position="4">
                    ДПК
                    <span class="resize-handle"></span>
                    <span class="sort-dpk-top">
                        <i data-order="date_last_communication" class="bi bi-caret-up-fill sort-button" id="sorting-date_last_communication-asc"></i>
                    </span>
                    <span class="sort-dpk-bottom">
                        <i data-order="-date_last_communication" class="bi bi-caret-down-fill sort-button" id="sorting-date_last_communication-asc"></i>
                    </span>
                </th>

                

                <th scope="col" rowspan="2" class="header-th-data header-th-sort-data" data-type="numeric-long" data-position="5">
                    Общая сумма в работе
                    <span class="resize-handle"></span>
                    <span class="sort-opportunity-work-top">
                        <i data-order="summa_by_company_work" class="bi bi-caret-up-fill sort-button"></i>
                    </span>
                    <span class="sort-opportunity-work-bottom">
                        <i data-order="-summa_by_company_work" class="bi bi-caret-down-fill sort-button"></i>
                    </span>
                </th>
                <th scope="col" rowspan="2" class="header-th-data header-th-sort-data" data-type="numeric-long" data-position="6">
                    Общая сумма успешных
                    <span class="resize-handle"></span>
                    <span class="sort-opportunity-sucсess-top">
                        <i data-order="summa_by_company_success" class="bi bi-caret-up-fill sort-button"></i>
                    </span>
                    <span class="sort-opportunity-sucсess-bottom">
                        <i data-order="-summa_by_company_success" class="bi bi-caret-down-fill sort-button"></i>
                    </span>
                </th>

                ${firstRowHTML}
            </tr>
            <tr class="text-center">
                ${secondRowHTML}
            </tr>
            <tr class="text-center">
                ${thirdRowHTML}
            </tr>
        `;
        return contentHTML       
    }

    // добавление данных в таблицу
    async renderTableBodyToHTML(data, dpk=NaN) {
        /* Подготовка контента и вставка его в таблицу */
        this.content = "";
        // `
        //     <tr>
        //         ${this.renderActiveDealRow(data)}
        //     </tr>
        // `;
        for (let company of data) {
            let companyDirectionContent = this.renderColumnDirectionHTML(company.direction, company.id_bx, company.name);
            let responsibleHTML = company.responsible_lastname ? `<a href=${company.responsible_url} target="_blank">${company.responsible_lastname} ${company.responsible_name || ''}</a>` : '&ndash;';
            
            let limitDate = new Date(dpk);
            let objDate = new Date(company.date_last_communication);
            const minDate = new Date(2000, 1);
            let insertDate = objDate > minDate ? objDate : NaN;
            let date = this.formatDate(insertDate);
            // let date = this.formatDate(company.date_last_communication);
            let dpkCellStyle = objDate > limitDate ? "" : "dpk-more-six-months"

            this.content += `
                <tr>
                    <td class="col-company" data-name='${company.name}' data-url='${company.url}' data-inn='${company.inn || ""}' data-id='${company.id_bx || ""}'>
                        <p><a href=${company.url} data-tooltip="HTML<br>подсказка" target="_blank">${company.name}</a></p>
                    </td>

                    <!-- <td>${company.inn || '&ndash;'}</td> -->
                    
                    <td class="col-responsible" data-name='${company.responsible_name || ""}' 
                                                data-lastname='${company.responsible_lastname}' 
                                                data-url='${company.responsible_url}'
                                                data-id='${company.responsible_id}'>
                        ${responsibleHTML}
                    </td>
                    
                    <td class='${dpkCellStyle}'>${date}</td>
                    
                    <td>${company.summa_by_company_work.toLocaleString()}</td>
                    
                    <td>${company.summa_by_company_success.toLocaleString()}</td>
                    
                    ${companyDirectionContent}
                </tr>
            `;
            // class='directory-column-border-right'
        }
        this.tableBody.innerHTML = await this.content;                // Вставляем контент в таблицу
    }

    // отрисовка строки с автивными сделками
    renderActiveDealRow(data) {
        let n = 6;                  // столбец с которого начинаются данные по направлениям
        let count = 2;              // столбцов в направлении
        let contentHtml = `
            <td class="col-company count-active-deal" style="grid-column: $1/2;">
        
            </td>
            <td scope="col" colspan="${n}" class="count-active-deal" style="grid-column: 2/${n};">
                <div>Активные сделки на странице</div>
            </td>
        `;
        let directions = data[0].direction;
        for (let index in directions) {
            let idDirBx = directions[index]["id_bx"]
            let keyActDealByDir = "dir_" + idDirBx;
            contentHtml += `
                <td scope="col" colspan="${count}" class="count-active-deal directory-column-border-left-border-left" style="grid-column: ${n}/${n + count};">
                    <div>${data[0][keyActDealByDir]}</div>
                </td>
            `;
            n += count;
        }
        return contentHtml;
        // style="grid-column: ${n}/${n + 3}; grid-row: 1/2"
    }

    // сумма сделок по одному направлению на одной странице
    getcountActiveDeal(data, index) {
        let count = 0;
        for (let company of data) {
            count += +company.direction[index]["count_deals"];
        }
        return count;
    }

    // принимает список направлений и возвращает их HTML код для вставки 
    // в таблицу (столбцы с данными по направлениям)
    renderColumnDirectionHTML(directions, id_company, name_company) {
        let contentDirection = '';
        for (let direction of directions) {
            let status = direction.status_summa_by_direction_work;
            // const allowedCreateDeals = status === "0" || status === 0 ? true : false;
            let fieldSummaWork = status;
            let styleCell = "";
            if (status === "2" || status === 2) {
                fieldSummaWork = direction.summa_by_direction_work.toLocaleString();
            }
            if (status === "3" || status === 3) {
                fieldSummaWork = 1;
                styleCell = "cell-background-red";
            }

            contentDirection += `
                <td class='cell-add-deal directory-column-border-left ${styleCell}' 
                    data-id_company='${id_company}' 
                    data-name_company='${name_company}' 
                    data-id_direction='${direction.id_bx}'
                    data-name_direction='${direction.name}'
                    data-id_category='43'
                    data-id_stage='C43:NEW'
                    data-allowed_add_deals=${status}
                >
                    ${fieldSummaWork}
                </td>
                <td class='cell-add-deal'
                    data-id_company='${id_company}'
                    data-name_company='${name_company}'  
                    data-id_direction='${direction.id_bx}'
                    data-name_direction='${direction.name}'
                    data-id_category='43'
                    data-id_stage='C43:NEW'
                    data-allowed_add_deals=${status}
                >
                    ${direction.summa_by_direction_success.toLocaleString()}
                </td>
            `;
            // <td>${direction.count_deals}</td>
        }
        return contentDirection;
    }

    // принимает список сделок и возвращает их HTML код для вставки в таблицу
    renderColumnDealsHTML(deals) {
        let contentDeals = '';
        for (let deal of deals) {
            contentDeals += `
                <li data-id=${deal.id_bx} 
                    data-url=${deal.url} 
                    data-name=${deal.title} 
                    data-datecreate=${deal.date_create} 
                    data-dateclosed=${deal.date_closed} 
                    data-datecommunication=${deal.date_last_communication} 
                    data-opportunity=${deal.opportunity} 
                    data-amount=${deal.amount_paid} 
                    data-closed=${deal.closed}>
                    <a href=${deal.url}>${deal.id_bx}</a>
                </li>`;
        }
        return contentDeals;
    }

    // принимает дату в формате ISO и возвращает дату в формате "дд.мм.гггг"
    formatDate(d) {
        if (!d) {
            return "&ndash;";
        }
        let date = new Date(d);
        let options = {
            year: 'numeric',
            month: 'numeric',
            day: 'numeric',
        };
        return date.toLocaleString("ru", options);
    }

    // обработчик событий наведения мыши на пользователя или компанию
    eventHoverElementsTable() {
        $("table").on('mouseover', (event) => {
            let colCompany = $(".col-company");
            if (event.target.tagName == "A" && colCompany.has(event.target).length !== 0) {
                let elemHeight = $(".prompt-full-company-data").height();
                let elemA = event.target.getBoundingClientRect();
                let x = elemA.left + elemA.width + 10;
                let y = elemA.top + 55 / 2 - elemHeight / 2 + $(document).scrollTop();
                let td = colCompany.has(event.target)[0];
                let obj = {
                    "name": td.dataset.name,
                    "inn": td.dataset.inn,
                    "id": td.dataset.id,
                };

                this.displayPromptCompany(obj, x, y);
                $(event.target).on('mouseout', (event) => {
                    console.log("mouseout");
                    $(".prompt-full-company-data").css({
                        "display": "none",
                    })
                })
            } 
        })

        // $("table").on('mouseover', (event) => {
        //     let colCompany = $(".col-responsible");
        //     if (event.target.tagName == "A" && colCompany.has(event.target).length !== 0) {
        //         let elemHeight = $(".prompt-full-responsible-data").height();
        //         let elemA = event.target.getBoundingClientRect();
        //         let x = elemA.left + elemA.width + 10;
        //         let y = elemA.top + 55 / 2 - elemHeight / 2 + $(document).scrollTop();
        //         let td = colCompany.has(event.target)[0];
        //         let obj = {
        //             "name": td.dataset.name,
        //             "lastname": td.dataset.lastname,
        //             "photo": td.dataset.photo,
        //             "url": td.dataset.url,
        //             "profession": td.dataset.profession,
        //             "id": td.dataset.id,
        //         };

        //         this.displayPromptResponsible(obj, x, y);
        //         $(event.target).on('mouseout', (event) => {
        //             console.log("mouseout");
        //             $(".prompt-full-responsible-data").css({
        //                 "display": "none",
        //             })
        //         })
        //     } 
        // })
    }
    
    // вывод каточки с данными компании
    displayPromptCompany(obj, x, y) {
        $(".prompt-data-company-name").text(obj.name);
        $(".prompt-data-company-inn span").text(obj.inn);
        $(".prompt-data-company-id-bx span").text(obj.id);

        $(".prompt-full-company-data").css({
            "display": "block",
            "position": "absolute",
            "left": x,
            "top": y
        })
    }

    // вывод карточки с данными пользователя
    displayPromptResponsible(obj, x, y) {
        // console.log("displayPromptResponsible = ", obj);
        $(".prompt-data-responsible-photo img").attr("src", obj.photo);
        $(".prompt-data-responsible-name").text(`${obj.lastname} ${obj.name}`);
        $(".prompt-data-responsible-profession span").text(obj.profession);
        $(".prompt-data-responsible-id span").text(obj.id);

        $(".prompt-full-responsible-data").css({
            "display": "flex",
            "position": "absolute",
            "left": x,
            "top": y
        })
    }
  
    date2str(d) 
    {
        return d.getFullYear() + '-' + paddatepart(1 + d.getMonth()) + '-' + paddatepart(d.getDate()) + 'T' + paddatepart(d.getHours()) + ':' + paddatepart(d.getMinutes()) + ':' + paddatepart(d.getSeconds()) + '+03:00';
    };
    
    // обработчик события создания сделки по двойному клику
    async eventAddDeal(data) {
        data['responsible'] = this.user;
        data['begindate'] = new Date();
        let isAddDeal = confirm(`Создать сделку в компании ${data['name_company']} по направлению ${data['name_direction']}?`);
        if (isAddDeal) {
            BX24.callMethod(
                'crm.company.contact.items.get',
                {id: data['company']},
                (result) => {
                    let response = result.data();
                    console.log("response deal = ", response);
                    if (response) {
                        data["items"] = response;
                        this.addDeal(data);
                    }
                }
            )
        }
    }

    // создание сделки в Битрикс
    addDeal(data) {
        // console.log("data999 = ", data);
        /* создание сделки в Bitrix */
        BX24.callMethod(
            'crm.deal.add', 
            {
                fields:
                    { 
                        "STAGE_ID": data['stage'],
                        "COMPANY_ID": data['company'],
                        "OPENED": "Y",
                        "ASSIGNED_BY_ID": data['responsible'],
                        "CATEGORY_ID": data['category'],
                        "UF_CRM_1610523951": data['direction'],
                    },
                params: { "REGISTER_SONET_EVENT": "Y" }	
            },
            (result)=> {
                let dealId = result.data();
                console.log("response deal = ", dealId);
                if (dealId && data["items"].length) {
                    BX24.callMethod(
                        'crm.deal.contact.items.set',
                        {
                            id: dealId,
                            items: data["items"]
                        },
                        (result) => {
                            let response = result.data();
                            console.log("response contact = ", response);
                            if (response) {
                                BX24.openPath(
                                    `/crm/deal/details/${dealId}/`,
                                    function(result)
                                    {
                                        console.log(result);
                                    }
                                );
            
                                data['target1'].dataset.allowed_add_deals = 1;
                                data['target2'].dataset.allowed_add_deals = 1;
                                data['element_sum_of_work'].innerHTML = "1";
                                return;
                            }
                        }
                    )
                } else if(dealId && !data["items"].length) {
                    BX24.openPath(
                        `/crm/deal/details/${dealId}/`,
                        function(result)
                        {
                            console.log(result);
                        }
                    );

                    data['target1'].dataset.allowed_add_deals = 1;
                    data['target2'].dataset.allowed_add_deals = 1;
                    data['element_sum_of_work'].innerHTML = "1";
                    return;
                } else {
                    alert("Не удалось создать сделку!");
                }
                
            }
        )
    }

    // получить ID текущего пользователя
    getCurrentUser() {
        BX24.callMethod('user.current', {}, (res) => {
            // console.log("user >>> ", res.data().ID);
            this.user = res.data().ID;
        });
    }
}