import React from 'react';
import { Link } from 'react-router';

/**
 * 404-ish view shown for routes that don't match any valid route.
 */
export default class NoMatch extends React.Component {
  render() {
    return (
      <div className="no-match fluid-8">
        <h2>Page Not Found</h2>
        <p>Sorry, we could not find the page you're looking for.</p>
        <p><Link to="/control/">Click here to return to the control index.</Link></p>
      </div>
    );
  }
}
