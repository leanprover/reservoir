<template>
  <div class="layout">
    <header class="gutter">
      <div class="contents top-line">
        <Logo class="compact"/>
        <SearchBar/>
        <NavLinks class="compact"/>
      </div>
    </header>
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
