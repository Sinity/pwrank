import { createApp, defineAsyncComponent } from "vue";

import PrimeVue from "primevue/config";
import ToastService from "primevue/toastservice";

import App from "./App.vue";
import router from "./router";

import "primevue/resources/themes/mdc-dark-indigo/theme.css";
import "primevue/resources/primevue.min.css";
import "primeflex/primeflex.min.css";

const app = createApp(App);

app.use(PrimeVue, { ripple: true });
app.use(ToastService);
app.use(router);

const components = {
  InputText: () => import("primevue/inputtext"),
  Button: () => import("primevue/button"),
  Menubar: () => import("primevue/menubar"),
  DataView: () => import("primevue/dataview"),
  DataViewLayoutOptions: () => import("primevue/dataviewlayoutoptions"),
  Dropdown: () => import("primevue/dropdown"),
  Dialog: () => import("primevue/dialog"),
  DataTable: () => import("primevue/datatable"),
  Column: () => import("primevue/column"),
  MultiSelect: () => import("primevue/multiselect"),
  Panel: () => import("primevue/panel"),
  Toast: () => import("primevue/toast"),
};

Object.entries(components).forEach(([name, loader]) => {
  app.component(name, defineAsyncComponent(loader));
});

app.mount("#app");
