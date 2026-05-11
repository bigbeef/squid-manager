Vue.component('admin-header', {
  template: `
    <el-header height="94px" class="admin-header">
      <div class="brand-block">
        <div class="brand-mark">S</div>
        <div>
          <div class="brand-title">Squid代理管理系统</div>
          <div class="brand-subtitle">后台管理中心</div>
        </div>
      </div>
      <div class="header-actions">
        <el-button size="small" type="danger" icon="el-icon-switch-button" @click="$emit('logout')">退出</el-button>
      </div>
    </el-header>
  `,
});

Vue.component('admin-sidebar', {
  props: {
    menus: {
      type: Array,
      required: true,
    },
    activeMenu: {
      type: String,
      required: true,
    },
  },
  template: `
    <el-aside width="220px" class="admin-aside">
      <div class="aside-title">系统菜单</div>
      <el-menu :default-active="activeMenu" class="admin-menu" @select="$emit('select', $event)">
        <el-menu-item v-for="item in menus" :key="item.key" :index="item.key">
          <i :class="item.icon"></i>
          <span slot="title">{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
  `,
});
