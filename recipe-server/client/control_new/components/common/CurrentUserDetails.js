import { Button } from 'antd';
import { Map } from 'immutable';
import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import { getCurrentUser } from 'control_new/state/serviceInfo/selectors';


@connect(
  state => ({
    user: getCurrentUser(state, Map()),
  }),
)
export default class CurrentUserDetails extends React.Component {
  static propTypes = {
    user: PropTypes.object.isRequired,
  }

  render() {
    const { user } = this.props;

    if (!user) {
      return null;
    }

    return (
      <div className="current-user">
        <span className="email">{user.get('email')}</span>

        <a href="/control/logout/">
          <Button type="primary" icon="logout" ghost>
            Log out
          </Button>
        </a>
      </div>
    );
  }
}
