import {templateSelectItemElement, templateUserBoxForSearch, templateDepartContainerBox, templateUserBoxForSelected, templateInputSearchUser} from '../templates/filter.js'


// Окно ПОИСК ПОЛЬЗОВАТЕЛЯ
export default class WindowSearchUser {
    constructor(container, bx) {
        this.container = container;
        // this.bx = new BX();
        this.bx = bx;
        this.timeAnimate = 100/100;     // скорость анимации разворачивания/сворачивания списка подразделений - мс./пикс.
        this.departContainer = this.container.querySelector(".container-data-depart");              // контейнер с подразделениями
        this.departChoiceContainer = this.container.querySelector(".container-data-head-selector"); // контейнер с выбранными
        this.departSearchInput = this.departChoiceContainer.querySelector("input");                 // контейнер ввода слова для поиска сотрудника
        
        this.boxResponsible = this.container.querySelector(".container-data-user");                 // окно ПОИСКА
        this.boxDepartment = this.container.querySelector(".container-data-depart");                // окно ПОДРАЗДЕЛЕНИЙ

        this.btnResponsible = this.container.querySelector(".btn-search-responsible");              // кнопка открыть "окно ПОИСК"
        this.btnDepartment = this.container.querySelector(".btn-search-department");                // кнопка открыть "окно ОТДЕЛЫ"


        
        this.departments = null;
    }

    async init() {
        await this.getDepartments();                                            // получение списка подразделений компаниии
        this.renderDepartment();                                                // вывод списка подразделений
        this.initHandler();                                                     // инициализация обработчиков
    }

    initHandler() {
        // событие "открытие окна поиска"
        this.btnResponsible.addEventListener("click", async (event) => {
            this.departChoiceContainer.querySelector("input").classList.remove("d-none")
            this.btnResponsible.classList.remove("btn-search-inactive");
            this.btnDepartment.classList.add("btn-search-inactive");
            this.boxResponsible.classList.remove("d-none");
            this.boxDepartment.classList.add("d-none");

        })
        // событие "открытие окна подразделения"
        this.btnDepartment.addEventListener("click", async (event) => {
            this.departChoiceContainer.querySelector("input").classList.add("d-none")
            this.btnResponsible.classList.add("btn-search-inactive");
            this.btnDepartment.classList.remove("btn-search-inactive");
            this.boxResponsible.classList.add("d-none");
            this.boxDepartment.classList.remove("d-none");
        })
      
        // событие "поиск пользователя"
        this.departChoiceContainer.addEventListener("input", async (event) => {
            if (event.target.closest(".search-user-input")) {
                let val = event.target.value;
                this.getAndDisplayUsersSearch(val);
            }
        })
        // событие "добавление пользователя в выбранные"
        this.container.addEventListener("click", async (event) => {
            let boxUser = event.target.closest(".ui-selector-user-box");            // блок-контейнер пользователя, по которому произошел клик
            // если клик не по кнопке "информация о сотруднике"
            if (boxUser && !event.target.closest(".ui-selector-item-user-link")) {
                let userId = boxUser.dataset.userId;
                let lastname = boxUser.dataset.lastname;
                let name = boxUser.dataset.name;
                let userType = boxUser.dataset.userType;

                this.addChoiceUser(userId, lastname, name, userType);
            }
        })
        // событие "клик разворачивание/сворачивание списка вложенных подразделений"
        this.departContainer.addEventListener("click", async (event) => {
            if (event.target.closest(".ui-selector-item-indicator")) {
                let box = event.target.closest(".ui-selector-item-box");            // блок-контейнер подразделения, по которому произошел клик
                let boxChildren = box.querySelector(".ui-selector-item-children");  // блок-контейнер с дочерними подразделениями родителя, по которому произошел клик
                let departId = box.dataset.departId;                                // id подразделения
                let usersDisplay = box.dataset.userDisplay;                         // список работников выведен/не выведен ("true"/"")
                if (!usersDisplay && departId) {
                    this.getAndDisplayUsersOfdepart(departId, boxChildren);         // получение и вывод списка работников подразделения
                    box.dataset.userDisplay = true;                                 // статус, что сотрудники подразделения уже выведены
                }
                if (box.classList.contains("ui-selector-item-box-open")) {
                    // свернуть вложенные подразделения
                    this.animationClose(boxChildren);
                    box.classList.remove("ui-selector-item-box-open");              // удаляем класс, что вложенные подразделения развернуты
                } else {
                    // развернуть вложенные подразделения
                    this.animationOpen(boxChildren);
                    box.classList.add("ui-selector-item-box-open");                 // добавляем класс, что вложенные подразделения развернуты
                }
            }
        })
        // событие "открытие страницы с информацией о сотруднике"
        this.container.addEventListener("click", async (event) => {
            if (event.target.classList.contains("ui-selector-item-user-link")) {
                let boxUser = event.target.closest(".ui-selector-user-box");            // блок-контейнер пользователя, по которому произошел клик
                let userId = boxUser.dataset.userId; 
                let path = `/company/personal/user/${userId}/`
                console.log(path);
                await this.bx.openPath(path);
            }
            if (event.target.closest(".user-item-content") && !event.target.classList.contains("user-item-remove")) {
                let boxUser = event.target.closest(".user-item");                       // блок-контейнер пользователя, по которому произошел клик
                let userId = boxUser.dataset.userId; 
                let path = `/company/personal/user/${userId}/`
                console.log(path);
                await this.bx.openPath(path); 
            }
            
        })

        // событие "удалить пользователя из выбранных"
        this.departChoiceContainer.addEventListener("click", async (event) => {
            if (event.target.closest(".user-item-remove")) {
                let boxUser = event.target.closest(".user-item");                       // блок-контейнер пользователя, по которому произошел клик
                boxUser.remove();
            }
        })
        // // событие "скрыть окно выбора пользователей"
        // document.addEventListener("click", async (event) => {
        //     if (!event.target.closest(".window-searchcontact") && !event.target.closest(".user-item-remove")) {
        //         this.hideWindow();
        //     }
        // })

    }

    showWindow(userConyainer, x, y) {
        this.userConyainer = userConyainer;
        
        this.container.classList.remove("d-none");
        let left = x - this.container.offsetWidth;
        let top = y + 50;
        this.container.style.left = Math.max(0, left) + "px";
        this.container.style.top = top + "px";
    }

    hideWindow() {
        this.container.classList.add("d-none");
    }

    // получение и вывод списка работников в окне поиска
    async getAndDisplayUsersSearch(value) {
        let contentHTML = "";
        let users = await this.bx.callMethod("user.search", {                             // получение списка пользователей подразделения из Битрикс
            "FILTER": {"NAME": `${value}%`, "ACTIVE": true}
        });
        let usersByLastname = await this.bx.callMethod("user.search", {                             // получение списка пользователей подразделения из Битрикс
            "FILTER": {"LAST_NAME": `${value}%`, "ACTIVE": true}
        });
        users.concat(usersByLastname);
        // let users = USERS;
        for (let user of users) {
            contentHTML += templateUserBoxForSearch(user.ID, user.LAST_NAME, user.NAME, user.WORK_POSITION, user.USER_TYPE);
        }
        this.boxResponsible.innerHTML = contentHTML;
    }

    // добавление пользователя в окно выбранных пользователей
    addChoiceUser(id, lastname, name, usertype) {
        let contentHTML = "";
        contentHTML += templateUserBoxForSelected(id, lastname, name, usertype);    // 
        contentHTML += templateInputSearchUser();                                   //
        this.departChoiceContainer.innerHTML = contentHTML;                         //
        this.userConyainer.innerHTML = templateUserForFieldResponsible(lastname, name);             //
        this.userConyainer.dataset.userId = id;
    }


    // <<<<<<<===== ДОБАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯ ЭКСТРАНЕТ =====>>>>>>>
    // возвращает данные из формы "ПРИГЛАШЕНИЕ ПОЛЬЗОВАТЕЛЯ"
    getDataFormInvite() {
        let email = this.form.email.value;
        let lastname = this.form.lastname.value;
        let name = this.form.name.value;
        return {
            LAST_NAME: lastname,
            NAME: name,
            EMAIL: email,
            GROUP_ID: "17"
        };
    }

    // добавление пользователя экстранет
    async addExtranetUser(user) {
        // добавление пользователя на портал
        let userId = await this.bx.callMethod("user.add", {                               
            "NAME": name, "LAST_NAME": lastname, "EMAIL": email, "EXTRANET": "Y", "SONET_GROUP_ID": [group]
        });
        // let userId = 49;
        return {
            ID: userId,
            NAME: user.NAME,
            LAST_NAME: user.LAST_NAME,
            EMAIL: user.EMAIL,
            EXTRANET: "Y",
            SONET_GROUP_ID: [user.GROUP_ID],
            UDER_TYPE: "extranet"
        };
    }


    // <<<<<<<===== ПОЛУЧЕНИЕ ДАННЫХ ПРИ ИНИЦИАЛИЗАЦИИ =====>>>>>>>
    // получение и вывод списка работников подразделения
    async getAndDisplayUsersOfdepart(departId, box) {
        let contentHTML = "";
        let users = await this.bx.callMethod("user.get", {                               // получение списка пользователей подразделения из Битрикс
            "ACTIVE": true, "UF_DEPARTMENT": departId, "ADMIN_MODE": true
        });
        // let users = USERS;
        for (let user of users) {
            contentHTML += templateUserBoxForSearch(user.ID, user.LAST_NAME, user.NAME, user.WORK_POSITION, user.USER_TYPE);
        }
        box.insertAdjacentHTML('beforeend', contentHTML);
    }

    // получение списка подразделений компаниии
    async getDepartments() {
        this.departments = await this.bx.callMethod("department.get");          // получение списка подразделений из Битрикс
        // this.departments = DEPART;
        this.companyStructure = this.getTreeDepartments();                          // структура кмпании
    }

    // возвращает иерархическую структуру компании
    getTreeDepartments(parent=undefined) {
        let departmentsList = [];                                               // список департаментов с родительским подразделений = "parent"
        if (!this.departments) return;
        for (let department of this.departments) {
            if (department.PARENT === parent) {
                let children = this.getTreeDepartments(department.ID);          // список дочерних подразделений
                if (children.length !== 0) {
                    department.CHILDREN = children;
                }
                departmentsList.push(department);
            }
        }
        return departmentsList;
    }


    // <<<<<<<===== ОТРИСОВКА ЭЛЕМЕНТОВ =====>>>>>>>
    // вывод списка подразделений
    renderDepartment() {
        this.boxDepartment.innerHTML = this.getHtmlDepartments(this.companyStructure);
    }

    // получить HTML код подразделений
    getHtmlDepartments(departments) {
        let contentHTML = '';
        for (let department of departments) {
            let departChildrenHTML = "";
            if (!department) return ""; 
            if (Array.isArray(department.CHILDREN) && department.CHILDREN.length >= 1) {
                departChildrenHTML += this.getHtmlDepartments(department.CHILDREN);
            }
            contentHTML += templateDepartContainerBox(department.ID, department.NAME, departChildrenHTML);
        }
        return contentHTML;
    }


    // <<<<<<<===== АНИМАЦИИ =====>>>>>>>
    // анимация разворачивания списка подразделений
    animationOpen(element) {
        let anime = element.animate({
            height: `${element.scrollHeight}px`}, this.timeAnimate //* element.scrollHeight
        );
        anime.addEventListener('finish', function() {
            element.style.height = '100%';
        });
        this.animate = anime;
    }

    // анимация сворачивания списка подразделений
    animationClose(element) {
        let height = element.offsetHeight || element.scrollHeight;
        element.style.height = `${height}px`;
        let anime = element.animate(
            {height: "0px"}, this.timeAnimate //* height
        )
        anime.addEventListener('finish', function() {
            element.style.height = '0px';
        });
        this.animate = anime;
    }

}