# batman-ms-stripe

## Overview
**batman-ms-stripe** is a microservice responsible for managing Stripe payments, subscriptions, invoices, and webhook events. It provides a RESTful API for handling customer operations, checkout sessions, and Stripe event processing.

This service plays a crucial role in payment processing by acting as an intermediary between the Stripe API and internal applications, ensuring seamless subscription management and transaction handling.

## Features
- **Customer Management**: Create, retrieve, and delete Stripe customers.
- **Subscription Handling**: Cancel active subscriptions.
- **Invoice Retrieval**: Fetch invoices for customers.
- **Payment Processing**: Create Stripe checkout sessions.
- **Event Handling**: Process webhook events from Stripe.

## API Endpoints

### Customer Management
#### Retrieve a Customer
```http
GET /api/v1/Stripe/Customer/Get
```
Retrieves details about a specific customer based on query parameters.

#### Delete a Customer
```http
POST /api/v1/Stripe/Customer/Delete
```
Deletes a Stripe customer based on the provided payload.

### Subscription Management
#### Cancel a Subscription
```http
POST /api/v1/Stripe/Subscription/Cancel
```
Cancels an active Stripe subscription.

### Invoice Handling
#### Retrieve Invoices
```http
GET /api/v1/Stripe/Invoices/Get
```
Fetches invoices associated with a specific customer.

### Payment Processing
#### Create Checkout Session
```http
POST /api/v1/Stripe/CheckoutSession/Create
```
Creates a Stripe checkout session for handling payments.

### Webhook Handling
#### Process Webhook Events
```http
POST /api/v1/Stripe/Webhook
```
Processes events received from Stripe webhooks.

## Integration with AWS SQS
In addition to direct webhook processing, **batman-ms-stripe** integrates with **batman-stripe-sqs**, a dedicated service that polls messages from an AWS SQS queue. This service:
- Continuously listens for incoming Stripe-related events.
- Forwards the retrieved messages to **batman-ms-stripe**'s webhook endpoint for processing.
- Ensures that event handling is robust, resilient, and scalable by decoupling Stripe webhook processing from direct event ingestion.

## Why Use This Service?
- Provides a structured API for managing Stripe transactions and subscriptions.
- Ensures payment-related events are processed reliably.
- Enhances scalability by leveraging AWS SQS for event polling.

## Final Thoughts
This service ensures that all Stripe interactions are handled efficiently, securely, and with the power of automation. Whether it's managing customers, processing invoices, or handling webhook events, **batman-ms-stripe** is Gotham's go-to payment orchestrator. 🦇💰

