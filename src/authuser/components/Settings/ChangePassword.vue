<template>
  <div class="edit-box">
    <q-field
      icon="fas fa-lock"
      :label="$t('USERDETAIL.PASSWORD')"
      :error="hasError('newPassword')"
      :error-label="firstError('newPassword')"
    >
      <q-input
        type="password"
        v-model="newPassword"
      />
    </q-field>
    <q-field
      icon="fas fa-unlock"
      :label="$t('USERDETAIL.OLD_PASSWORD')"
      :error="hasError('oldPassword')"
      :error-label="firstError('oldPassword')"
    >
      <q-input
        type="password"
        v-model="oldPassword"
      />
    </q-field>

    <div
      v-if="hasNonFieldError"
      class="text-negative"
    >
      {{ firstNonFieldError }}
    </div>

    <div class="actionButtons">
      <q-btn
        color="primary"
        @click="save"
        :disable="!hasNewPassword || !hasOldPassword || !hasPasswordChanged"
        :loading="isPending"
      >
        {{ $t('BUTTON.CHANGE_PASSWORD') }}
      </q-btn>
    </div>
  </div>
</template>

<script>
import { QField, QInput, QBtn } from 'quasar'
import statusMixin from '@/utils/mixins/statusMixin'

export default {
  components: { QField, QInput, QBtn },
  mixins: [statusMixin],
  computed: {
    hasNewPassword () {
      return !!this.newPassword
    },
    hasOldPassword () {
      return !!this.oldPassword
    },
    hasPasswordChanged () {
      return this.oldPassword !== this.newPassword
    },
  },
  data () {
    return {
      oldPassword: '',
      newPassword: '',
    }
  },
  methods: {
    reset () {
      this.oldPassword = ''
      this.newPassword = ''
    },
    save () {
      const { oldPassword, newPassword } = this
      this.$emit('save', { oldPassword, newPassword, done: this.reset })
    },
  },
}
</script>

<style scoped lang="stylus">
@import '~editbox'
</style>
