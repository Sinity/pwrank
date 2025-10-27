import { createRouter, createWebHistory } from "vue-router";
import { REST } from "../rest";

const routes = [
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/LoginPage.vue"),
  },
  {
    path: "/rankings",
    alias: "/",
    name: "Rankings",
    component: () => import("../views/RankingsPage.vue"),
  },
  {
    path: "/ranking/:id",
    name: "Ranking",
    component: () => import("../views/RankingPage.vue"),
  },
  {
    path: "/compare/:id",
    name: "Comparing",
    component: () => import("../views/ComparePage.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL || "/"),
  routes,
});

const PUBLIC_ROUTES = new Set(["/login"]);

router.beforeEach((to) => {
  if (!PUBLIC_ROUTES.has(to.path) && !REST.userIdentity()) {
    return {
      path: "/login",
      query: to.fullPath !== "/login" ? { redirect: to.fullPath } : {},
    };
  }
});

export default router;
