
export default class Paginator {
    constructor(container) {
        this.container = container;
        this.currentPageNumber = 1;

    }

    initHandler() {
        this.container.addEventListener('click', async (e) => {
            if (e.target.tagNmae === "A") {
                let page = parseInt(e.target.dataset.page);
            }
            let page = event.target.dataset.page;
            if (page) {
                // устанавливаем требуемую страницу для получения данных
                this.page = +page;
                // получение данных статистики и вывод их в таблицу
                this.getData();
            }
        });
        this.paginatorContent.onclick = (event) => {
            let page = event.target.dataset.page;
            if (page) {
                // устанавливаем требуемую страницу для получения данных
                this.page = +page;
                // получение данных статистики и вывод их в таблицу
                this.getData();
            }
        };
    }



}

