<template>
  <div class="layout">
    <div class="bg-top-line" />
    <NavBar/>
    <main>
        <slot/>
    </main>
    <footer class="gutter">
      <FooterLinks class="contents"/>
    </footer>
  </div>
</template>

<style scoped>

main {
      margin-top: 0px;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.bg-top-line {
  background: linear-gradient(to right, #2987DA, #1C74C1);
  height: 10px;
}

</style>