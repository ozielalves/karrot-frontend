<script>
import { connect } from 'vuex-connect'
import VerifyMail from '@/authuser/components/VerifyMail'

export default connect({
  gettersToProps: {
    status: 'verifymail/verifyStatus',
    success: 'verifymail/success',
  },
  lifecycle: {
    // when page is loaded, use the `?code` route parameter to trigger verification
    mounted: ({ getters, dispatch }) => dispatch('verifymail/verify', getters['route/query'].code),
  },
})('VerifyMail', VerifyMail)
</script>
