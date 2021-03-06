<template>
  <div class="list-wrapper">
    <q-list
      no-border
    >
      <q-item
        v-if="users.length > 15"
      >
        <q-search v-model="filterTerm" />
      </q-item>
      <UserItem
        v-for="user in activeUsers"
        :key="user.id"
        :user="user"
        :group="group"
        @createTrust="$emit('createTrust', arguments[0])"
      />
      <q-item-separator />
      <q-collapsible
        v-if="inactiveUsers.length > 0"
        icon="fas fa-bed"
        :label="$t('GROUP.INACTIVE')"
        :sublabel="inactiveSublabel"
        @show="showInactive = true"
        @hide="showInactive = false"
      >
        <template v-if="showInactive">
          <UserItem
            v-for="user in inactiveUsers"
            :key="user.id"
            :user="user"
            :group="group"
            class="inactive"
            @createTrust="$emit('createTrust', arguments[0])"
          />
        </template>
      </q-collapsible>
    </q-list>
  </div>
</template>

<script>
import {
  QList,
  QListHeader,
  QItemSeparator,
  QItem,
  QCollapsible,
  QSearch,
} from 'quasar'

import UserItem from './UserItem'

export default {
  components: {
    UserItem,
    QList,
    QListHeader,
    QItemSeparator,
    QItem,
    QCollapsible,
    QSearch,
  },
  props: {
    users: {
      type: Array,
      required: true,
    },
    group: {
      type: Object,
      default: null,
    },
    sorting: {
      type: String,
      default: 'joinDate',
    },
  },
  data () {
    return {
      showInactive: false,
      filterTerm: '',
    }
  },
  methods: {
    sort (list) {
      const getJoinDate = a => a.membership.createdAt
      const sortByJoinDate = (a, b) => getJoinDate(b) - getJoinDate(a)
      const sortByName = (a, b) => a.displayName.localeCompare(b.displayName)
      return list.slice().sort(this.sorting === 'joinDate' ? sortByJoinDate : sortByName)
    },
    filterByTerms (list) {
      if (!this.filterTerm || this.filterTerm === '') return list
      return list.filter(u => u.displayName.toLowerCase().includes(this.filterTerm.toLowerCase()))
    },
  },
  computed: {
    inactiveSublabel () {
      return this.inactiveUsers.length + ' ' + this.$tc('JOINGROUP.NUM_MEMBERS', this.inactiveUsers.length)
    },
    activeUsers () {
      return this.sort(this.filterByTerms(this.users.filter(u => u.membership.active)))
    },
    inactiveUsers () {
      return this.sort(this.filterByTerms(this.users.filter(u => !u.membership.active)))
    },
  },
}
</script>

<style scoped lang="stylus">
.list-wrapper
  .profilePic
    margin-right .5em
.inactive
  opacity 0.5
</style>
