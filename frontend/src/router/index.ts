import { createRouter, createWebHistory } from 'vue-router'
import GuestLayout from '@/layouts/GuestLayout.vue'
import Login from '@/pages/Login.vue'
import StaffScanner from '@/pages/StaffScanner.vue'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: Login
  },
  {
    path: '/guest',
    component: GuestLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'personal',
        name: 'guest-personal',
        component: () => import('@/pages/GuestPersonal.vue')
      },
      {
        path: 'voucher',
        name: 'guest-voucher',
        component: () => import('@/pages/GuestVoucher.vue')
      }
    ]
  },
  {
    path: '/employee',
    name: 'employee',
    component: StaffScanner,
    meta: { requiresAuth: true, requiresEmployee: true }
  },
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Добавляем навигационный guard
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  console.log('Navigation guard:', {
    to: to.path,
    from: from.path,
    isAuthenticated: userStore.isAuthenticated,
    isEmployee: userStore.isEmployee,
    telegram_id: userStore.telegram_id
  })
  
  // В режиме разработки можем включить/отключить принудительную авторизацию
  const skipAuthInDev = false // Установить true, чтобы пропускать авторизацию в режиме разработки
  
  if (import.meta.env.DEV && skipAuthInDev && to.path.startsWith('/guest')) {
    console.log('Режим разработки: пропускаем авторизацию для гостевых страниц')
    next()
    return
  }
  
  // Если маршрут требует авторизации и пользователь не авторизован
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    console.log('Редирект на страницу логина: пользователь не авторизован')
    next('/login')
    return
  }
  
  // Если маршрут требует прав сотрудника, но пользователь не сотрудник
  if (to.meta.requiresEmployee && !userStore.isEmployee) {
    console.log('Редирект на гостевую страницу: у пользователя нет прав сотрудника')
    next('/guest/voucher')
    return
  }
  
  // Если пользователь авторизован и пытается зайти на страницу логина
  if (userStore.isAuthenticated && to.path === '/login') {
    console.log('Редирект на страницу в соответствии с ролью: пользователь уже авторизован')
    if (userStore.isEmployee) {
      next('/employee')
    } else {
      next('/guest/voucher')
    }
    return
  }
  
  console.log('Продолжаем навигацию на:', to.path)
  next()
})

export default router
