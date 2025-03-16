// Import required modules
import { serve } from "jsr:@supabase/functions-js";
import nodemailer from "npm:nodemailer";

// Start the Supabase function
serve(async (req) => {
  try {
    // Extract data from the request
    const { email, subject, message, product_url } = await req.json();

    // Validate required fields
    if (!email || !subject || !message || !product_url) {
      return new Response(
        JSON.stringify({ error: "Missing required fields" }),
        { status: 400 }
      );
    }

    // Configure nodemailer with your email service
    const transporter = nodemailer.createTransport({
      service: "gmail",
      auth: {
        user: Deno.env.get("EMAIL_USER"),
        pass: Deno.env.get("EMAIL_PASS"),
      },
    });

    // Email content
    const mailOptions = {
      from: Deno.env.get("EMAIL_USER"),
      to: email,
      subject,
      html: `
        <p>${message}</p>
        <br>
        <a href="${product_url}" target="_blank">View Product</a>
      `,
    };

    // Send the email
    await transporter.sendMail(mailOptions);

    return new Response(JSON.stringify({ success: true }), { status: 200 });
  } catch (error) {
    console.error("Error sending email:", error);
    return new Response(
      JSON.stringify({ error: "Internal Server Error" }),
      { status: 500 }
    );
  }
});
