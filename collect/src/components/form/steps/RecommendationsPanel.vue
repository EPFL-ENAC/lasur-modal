<template>
  <div v-if="collector.loadingTypo">
    <q-spinner-grid color="primary" size="50px" />
  </div>
  <div v-else>
    <RecommendationsPersoPanel />
    <RecommendationsProPanel class="q-mt-xl" />
  </div>
</template>

<script setup lang="ts">
import RecommendationsPersoPanel from 'src/components/form/steps/RecommendationsPersoPanel.vue'
import RecommendationsProPanel from 'src/components/form/steps/RecommendationsProPanel.vue'

const collector = useCollector()
</script>
