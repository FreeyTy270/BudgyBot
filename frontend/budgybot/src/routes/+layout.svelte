<script lang="ts">
  import './layout.css';
  import {Navbar, NavBrand, NavLi, NavUl, NavHamburger, DarkMode} from "flowbite-svelte";
  import {page} from "$app/state";
  import budgy from '$lib/assets/budgy.png';

  let {children} = $props();
  let activeUrl = $derived(page.url.pathname);
</script>

<svelte:head>
  <link rel="icon" href={budgy}/>
</svelte:head>

<main class="dark:bg-primary-900">
  <DarkMode/>
  <header>
    <Navbar>
      <NavBrand href="/">
        <img src={budgy} class="me-3 h-6 sm:h-9" alt="Budgy Portrait">
        <span class="self-center text-xl font-semibold whitespace-nowrap dark:text-white">BudgyBot</span>
      </NavBrand>
      <NavHamburger/>
      <NavUl {activeUrl}>
        <NavLi href="/" class="btn">Overview</NavLi>
        <NavLi href="/Budget" class="btn">Budget</NavLi>
        <NavLi href="/Banks" class="btn">Banks</NavLi>
      </NavUl>
    </Navbar>
  </header>

  {@render children()}

</main>