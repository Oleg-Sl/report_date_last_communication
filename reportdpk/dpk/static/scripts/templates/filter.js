// html-шаблон карточки компании из окна выбора
function templateCartCompanyElement(id_bx, name, inn) {
    return `
        <div class="filter-window-cart" data-id-bx="${id_bx}" data-inn="${inn}" data-name="${name}">
            <div class="filter-window-cart-name" title="${name}">${name}</div>
            <div class="filter-window-cart-inn"><b>ИНН:</b> ${inn}</div>
            <div class="filter-window-cart-id-bx"><b>ID в BX24:</b> ${id_bx}</div>
        </div>
    `;
}

// html-шаблон карточки направления сделки из окна выбора
function templateCartDirectionElement(id_bx, name) {
    return `
        <li class="list-group-item">
            <input class="form-check-input me-1" type="checkbox" data-id-bx="${id_bx}" value="${name}" aria-label="...">${name}
        </li>
    `;
}

// html-шаблон карточки направления сделки из окна выбора
function templateItemSingle(name) {
    return `
        <li class="" data-name="${name}">
            ${name}
        </li>
    `;
}

// html-шаблон элемента фильтра множественного выбора
function templateSelectItemElement(id_bx, name) {
    return `
        <div class="filter-item" data-id-bx="${id_bx}" data-name="${name}">
            <div class="filter-item-name" title="${name}">${name}</div>
            <div class="filter-item-delete"><button type="button" class="btn-close" aria-label="Close"></button></div>
        </div>
    `;
}



export {templateCartCompanyElement, templateCartDirectionElement, templateItemSingle, templateSelectItemElement, };

