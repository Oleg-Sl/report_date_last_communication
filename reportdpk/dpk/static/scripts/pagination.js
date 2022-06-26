
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

        });
    }

    highlightPageNumber(page) {
        
    }

}

