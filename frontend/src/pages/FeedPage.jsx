import Layout from "../components/Layout";
import Feed from "../components/Feed";

export default function FeedPage() {
  return (
    <Layout>
      <h1 className="h1">Feed</h1>
      <p className="p-muted">Postagens de quem você segue</p>
      <div className="hr" />
      <Feed />
    </Layout>
  );
}
