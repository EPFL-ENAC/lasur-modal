<template>
  <q-footer class="footer q-py-lg q-px-xl">
    <div>
      <a href="https://epfl.ch" target="_blank" rel="noopener noreferrer"
        ><img src="/admin/EPFL.svg" alt="EPFL"
      /></a>
      <q-markdown :src="t('footer.epfl')" />
    </div>
  </q-footer>
</template>

<script setup lang="ts">
const { t } = useI18n()
</script>

<style scoped>
.footer {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
}
.footer > div {
  display: flex;
  flex-direction: column;
  align-items: start;
}
.footer img {
  height: 2rem;
  margin-bottom: 1rem;
}

:deep(a) {
  color: var(--q-primary) !important;
}
</style>
