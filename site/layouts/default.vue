<template>
  <div class="layout">
    <NavBar/>
    <main>
      <div class="contents">
        <slot/>
      </div>
    </main>
    <footer class="gutter">
      <FooterLinks class="contents"/>
    </footer>
  </div>
</template>

<style scoped>

main {
    margin-top: 0px;
}

.bg-top-line {
  background: linear-gradient(to right, #2987DA, #1C74C1);
  height: 10px;
}

</style>